from motor.core import AgnosticClientSession
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from datetime import datetime, timezone

from ....utils.exceptions import NotFoundException
from ....utils.simple_result import SimpleOkResult, SimpleErrorResult, SimpleResult
from ...models.banking.user_banking_account import UserBankingAccountDB
from ...models.banking.transaction import TransactionDB, TransactionType

COLLECTION = "userBankingAccounts"

class UserBankingAccountsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def get_collection(self) -> AsyncIOMotorCollection:
        return self.db[COLLECTION]

    async def create_account(self, user_id: int) -> SimpleResult[UserBankingAccountDB]:
        user_doc = await self.get_collection().find_one({"owner": user_id})
        if not user_doc:
            new_account = UserBankingAccountDB(
                accountId=str(user_id), #todo: real account id
                balance=0,
                owner=user_id,
                transactions=list(),
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
            try:
                result = await self.get_collection().insert_one(new_account.model_dump())
                if result.acknowledged:
                    new_account.id = result.inserted_id
                    return SimpleOkResult(payload=new_account)
                else:
                    return SimpleErrorResult(message=f"Unknown error:")
            except Exception as e:
                return SimpleErrorResult(message=str(e))
        else:
            return SimpleErrorResult(message=f"Event account for {user_id} already exists")

    async def get_account_by_user_id(self, user_id: int) -> SimpleResult[UserBankingAccountDB]:
        user_doc = await self.get_collection().find_one({"owner": user_id})
        if not user_doc:
            raise NotFoundException()
        else:
            try:
                account = UserBankingAccountDB(**user_doc)
                return SimpleOkResult(payload=account)
            except Exception as e:
                return SimpleErrorResult(message="Event account parsing error: " + str(e))

    async def get_account_by_account_id(self, account_id: str) -> SimpleResult[UserBankingAccountDB]:
        user_doc = await self.get_collection().find_one({"accountId": account_id})
        if not user_doc:
            return SimpleErrorResult(message=f"Event account for {account_id} not found")
        else:
            try:
                account = UserBankingAccountDB(**user_doc)
                return SimpleOkResult(payload=account)
            except Exception as e:
                return SimpleErrorResult(message="Event account parsing error: " + str(e))

    async def form_transaction_without_write(self, transaction: TransactionDB, account_id: str) -> SimpleResult[UserBankingAccountDB]:
        result = await self.get_account_by_account_id(account_id)
        if isinstance(result, SimpleOkResult):
            account = result.payload
            if transaction.type == TransactionType.withdraw:
                if transaction.amount > account.balance:
                    return SimpleErrorResult(message=f"Amount exceeds balance")
                else:
                    account.balance -= transaction.amount
                    account.transactions.append(transaction)
                    return SimpleOkResult(payload=account)
            if transaction.type == TransactionType.deposit:
                account.balance += transaction.amount
                account.transactions.append(transaction)
                return SimpleOkResult(payload=account)
            return SimpleOkResult(payload=result)
        else:
            return SimpleErrorResult(message=result.message)

    async def commit_formed_transaction(self, account: UserBankingAccountDB, session: AgnosticClientSession | None):
        account.updated_at = datetime.now(tz=timezone.utc)
        update_data = account.model_dump(exclude_unset=True)
        await self.get_collection().update_one(
            {"_id": account.id},
            {"$set": update_data},
            session=session)