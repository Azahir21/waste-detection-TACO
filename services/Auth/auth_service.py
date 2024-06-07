import asyncio
from fastapi import HTTPException
from fastapi.params import Depends
from repositories.Auth.auth_repository import AuthRepository
from services.Auth.jwt_service import JWTService
from services.Auth import security_service
from config.schemas.auth_schema import InputUser, InputLogin, OutputProfile
from config.schemas.commond_schema import TokenData


class AuthServices:
    def __init__(
        self,
        auth_repository: AuthRepository = Depends(),
        jwt_service: JWTService = Depends(),
    ):
        self.auth_repository = auth_repository
        self.jwt_service = jwt_service
        self.security_service = security_service

    async def insert_new_user(self, input_user: InputUser):
        found_duplicate_username = await self.auth_repository.find_user_by_username(
            input_user.username
        )

        found_duplicate_email = await self.auth_repository.find_user_by_email(
            input_user.email
        )
        print("log")
        if found_duplicate_username:
            raise HTTPException(status_code=404, detail="Username already exists")
        if found_duplicate_email:
            raise HTTPException(status_code=404, detail="Invalid Email or Password")
        input_user.password = self.security_service.get_password_hash(
            input_user.password
        )
        return await self.auth_repository.insert_new_user(input_user)

    async def login_user(self, input_login: InputLogin):
        found_user = await self.auth_repository.find_user_by_email(input_login.email)

        if found_user is None:
            raise HTTPException(status_code=404, detail="Invalid Email or Password")
        if not self.security_service.verify_password(
            input_login.password,
            found_user.password,
        ):
            raise HTTPException(status_code=404, detail="Invalid Email or Password")
        jwt_token = self.jwt_service.create_access_token(
            TokenData(
                userID=found_user.id.__str__(),
                name=found_user.username,
            ).dict()
        )
        return jwt_token

    async def get_current_user(self, tokenData: TokenData):
        try:
            found_user = await self.auth_repository.find_user_by_username(
                tokenData.name
            )
            return OutputProfile(username=found_user.username, email=found_user.email)
        except Exception as e:
            raise HTTPException(status_code=404, detail="Invalid Token")
