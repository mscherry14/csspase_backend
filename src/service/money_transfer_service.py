from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from src.database.models.banking.transaction import TransactionDB, TransactionType
from src.database.repositories.banking.event_banking_accounts_repository import EventBankingAccountsRepository
from src.database.repositories.banking.user_banking_accounts_repository import UserBankingAccountsRepository


class MoneyTransferService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    # TODO: remove this todo after shop account completing
    async def shop_transfer_money(self, session: AsyncIOMotorClientSession, from_acc: str, to_acc: str, amount: int,
                                  operation_id: str) -> None:
        """
        для того чтобы операции выполнились в рамках одной транзакции: передай сессию со start_transaction
        осторожно: по питоновским традициям бросается исключениями для отмены транзакции
        и надо их ловить
        """
        transaction_from = TransactionDB(amount=amount,
                                         type=TransactionType.withdraw,
                                         operation_id=operation_id)
        # transactionTo = TransactionDB() #TO SHOP TRANSACTION
        await UserBankingAccountsRepository(db=self.db).do_transaction(session=session, transaction=transaction_from,
                                                                       account_id=from_acc)
        # # Зачисление в магазин
        # await to_collection.update_one(
        #     {"_id": to_acc},
        #     {"$inc": {"balance": amount}},
        #     session=session,
        # )



    async def event_to_user_transfer_money(self, session: AsyncIOMotorClientSession, from_acc: str, to_acc: str, amount: int,
                                  operation_id: str) -> None:
        """
        для того чтобы операции выполнились в рамках одной транзакции: передай сессию со start_transaction

        осторожно: по питоновским традициям бросается исключениями для отмены транзакции
        и надо их ловить
        """
        transaction_from = TransactionDB(amount=amount,
                                         type=TransactionType.withdraw,
                                         operation_id=operation_id)
        transaction_to = TransactionDB(amount=amount,
                                         type=TransactionType.deposit,
                                         operation_id=operation_id)
        await EventBankingAccountsRepository(db=self.db).do_transaction(session=session, transaction=transaction_from,
                                                                        account_id=from_acc)
        await UserBankingAccountsRepository(db=self.db).do_transaction(session=session, transaction=transaction_to,
                                                                       account_id=to_acc)
