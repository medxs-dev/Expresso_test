from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "9eb5d957c411fc2ecd9afdb92464134685011988fbb6b4d919a6d3c723b6c49b922b914f390f79aa6b303119b5fc9b5d22536f29377b4822fa37309add6152f851f02354efd12f4f933001114f89f0ebb1a6f4f7f32bf566ed1cc20312dc791859df930e1233e10790379aa0a1a2195021e18720ded72ac5b3eb40d135a545f6072d64f6e9ab19e5a8fef11030dfb736285ff66ee32008c4f88f44043a91d1d66c576eed20ed43dbd9fc53809b778f2767d08a46137366795b184ac3b7875317b311057829b137b62cafd9d7283b2e16e8daf6a61a14f67104cc67b11132b12f2043ca7bebe47db803ea2af557061f432f6fcde41f3e50012632dfccfcc9b715"  # Change this to a strong secret in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgre@localhost/expresso_db_final"

    # DATABASE_URL: str = "postgresql+asyncpg://postgres:postgre@localhost/exp_demo"
    # DATABASE_URL: str = "postgresql+asyncpg://postgres:postgre@localhost/expresso_project"


settings = Settings()
