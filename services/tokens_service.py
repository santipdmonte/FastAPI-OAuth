from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from models.token_models import TokenBlocklist, TokenType


class TokenService:
    def __init__(self, db: Depends(get_db)):
        self.db = db

    def is_blacklisted(self, jti: str) -> bool:
        return (
            self.db.query(TokenBlocklist)
            .filter(TokenBlocklist.jti == jti)
            .first()
            is not None
        )

    def blacklist_token(
        self,
        *,
        jti: str,
        token_type: TokenType,
        user_id: Optional[UUID],
        expires_at: datetime,
        reason: Optional[str] = None,
    ) -> TokenBlocklist:
        if self.is_blacklisted(jti):
            return (
                self.db.query(TokenBlocklist)
                .filter(TokenBlocklist.jti == jti)
                .first()
            )

        entry = TokenBlocklist(
            jti=jti,
            token_type=token_type.value if hasattr(token_type, "value") else str(token_type),
            user_id=user_id,
            expires_at=expires_at,
            reason=reason,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry


def get_token_service(db: Session = Depends(get_db)) -> TokenService:
    return TokenService(db)


