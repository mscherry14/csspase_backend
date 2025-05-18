from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection, AsyncIOMotorClientSession
from datetime import datetime, timezone

from ....utils.exceptions import TransactionException
from ....utils.simple_result import SimpleOkResult, SimpleErrorResult, SimpleResult
from ...models.banking.event_banking_account import EventBankingAccountDB
from ...models.banking.transaction import TransactionDB, TransactionType

COLLECTION = "eventBankingAccounts"
DEFAULT_INIT_BALANCE=1500

class EventBankingAccountsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def get_collection(self) -> AsyncIOMotorCollection:
        return self.db[COLLECTION]

    async def create_account(self, event_id: str, init_balance: int, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[EventBankingAccountDB]:
        event_doc = await self.get_collection().find_one({"event": event_id}, session=session)
        if not event_doc:
            new_account = EventBankingAccountDB(
                accountId=event_id, #todo: real account id
                balance=init_balance,
                init_balance=init_balance,
                event=event_id,
                transactions=list(),
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
            try:
                result = await self.get_collection().insert_one(new_account.model_dump(exclude_none=True, exclude_unset=True), session=session)
                if result.acknowledged:
                    new_account.id = result.inserted_id
                    return SimpleOkResult(payload=new_account)
                else:
                    return SimpleErrorResult(message=f"Unknown error:")
            except Exception as e:
                return SimpleErrorResult(message=str(e))
        else:
            return SimpleErrorResult(message=f"Event account for {event_id} already exists")

    async def get_account_by_event_id(self, event_id: str, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[EventBankingAccountDB]:
        event_doc = await self.get_collection().find_one({"event": event_id}, session=session)
        if not event_doc:
            res = await self.create_account(event_id=event_id, init_balance=DEFAULT_INIT_BALANCE,session=session)
            if isinstance(res, SimpleErrorResult):
                return SimpleErrorResult(message="no acc found, trying to create with error: "+ res.message)
            return SimpleOkResult(payload=res.payload)
        else:
            try:
                account = EventBankingAccountDB(**event_doc)
                return SimpleOkResult(payload=account)
            except Exception as e:
                return SimpleErrorResult(message="Event account parsing error: " + str(e))

    async def get_account_by_account_id(self, account_id: str, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[EventBankingAccountDB]:
        user_doc = await self.get_collection().find_one({"accountId": account_id}, session=session)
        if not user_doc:
            return SimpleErrorResult(message=f"Event account for {account_id} not found")
        else:
            try:
                account = EventBankingAccountDB(**user_doc)
                return SimpleOkResult(payload=account)
            except Exception as e:
                return SimpleErrorResult(message="Event account parsing error: " + str(e))

    async def do_transaction(self, transaction: TransactionDB, account_id: str, session: AsyncIOMotorClientSession) -> None:
        result = await self.get_account_by_account_id(account_id, session=session)
        if isinstance(result, SimpleOkResult):
            account = result.payload
            if transaction.type == TransactionType.withdraw:
                if transaction.amount > account.balance:
                    raise TransactionException("not enough balance")
                else:
                    account.balance -= transaction.amount
            elif transaction.type == TransactionType.deposit:
                raise TransactionException("you cant increase event balance")
            transaction.created_at = datetime.now(tz=timezone.utc)
            account.transactions.append(transaction)
            account.updated_at = datetime.now(tz=timezone.utc)
            update_data = account.model_dump(exclude_unset=True, exclude_none=True)
            res = await self.get_collection().update_one(
                {"_id": account.id},
                {"$set": update_data},
                session=session)
            if not res.modified_count:
                raise TransactionException("unknown error while updating account")
        else:
            raise TransactionException("account not found")