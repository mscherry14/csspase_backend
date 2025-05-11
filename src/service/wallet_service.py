from typing import List

from ..database.models.banking.transaction import TransactionDB
from ..database.models.banking.user_banking_account import UserBankingAccountDB
from ..database.repositories.banking.user_banking_accounts_repository import UserBankingAccountsRepository
from ..database.repositories.users_repository import UsersRepository
from ..utils.exceptions import NotFoundException
from ..utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult

from motor.motor_asyncio import AsyncIOMotorDatabase


class WalletService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def _create_user_bank_account(self, user_id: int) -> SimpleResult[UserBankingAccountDB] :
        """
        1. Ищем юзера
        2. Проверяем наличие аккаунта
        3. Говорим "ой ошибочка" если акк есть и пушим нулевой акк и возвращаем его,
           если аккаунта нет
        """
        res = await UsersRepository(db=self.db).get_by_user_id(user_id=user_id)
        if isinstance(res, SimpleErrorResult):
            return SimpleErrorResult(message=res.message)
        else:
            try:
                result = await UserBankingAccountsRepository(db=self.db).get_account_by_user_id(user_id=user_id)
                return SimpleErrorResult(message="account already exists (if you still cant receive account it is parsing error)")
            except NotFoundException as e:
                res = await UserBankingAccountsRepository(db=self.db).create_account(user_id=user_id)
                return res

    async def _find_account(self, user_id: int) -> SimpleResult[UserBankingAccountDB]:
        """
        1. Ищем юзера
        2. Ищем его аккаунт
            2.1 если аккаунта нет, создаем нулевой(?) (_create_user_bank_account)
        """
        res = await UsersRepository(db=self.db).get_by_user_id(user_id=user_id)
        if isinstance(res, SimpleErrorResult):
            return SimpleErrorResult(message=res.message)
        else:
            try:
                result = await UserBankingAccountsRepository(db=self.db).get_account_by_user_id(user_id=user_id)
                return result
            except NotFoundException as e:
                res = await self._create_user_bank_account(user_id=user_id)
                return res

    async def get_user_balance(self, user_id: int) -> SimpleResult[int] :
        """
        _find_account()
        3. возвращаем баланс
        """
        res = await self._find_account(user_id=user_id)
        if isinstance(res, SimpleErrorResult):
            return SimpleErrorResult(message=res.message)
        return SimpleOkResult(payload=res.payload.balance)


    async def get_user_transactions(self, user_id: int) -> SimpleResult[List[TransactionDB]] :
        """
        _find_account()
            2.1 если аккаунта нет, создаем нулевой(?)
        3. возвращаем историю транзакций
        """
        res = await self._find_account(user_id=user_id)
        if isinstance(res, SimpleErrorResult):
            return SimpleErrorResult(message=res.message)
        return SimpleOkResult(payload=res.payload.transactions)