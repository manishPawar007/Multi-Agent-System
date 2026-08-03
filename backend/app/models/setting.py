from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base

class UserSetting(Base):
    __tablename__ = "settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    default_provider: Mapped[str] = mapped_column(String(50), default="ollama")
    default_model: Mapped[str] = mapped_column(String(100), default="qwen3")
    embedding_model: Mapped[str] = mapped_column(String(100), default="nomic-embed-text")
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2048)
    top_p: Mapped[float] = mapped_column(Float, default=0.95)

    # API Keys & URLs
    gemini_key: Mapped[str] = mapped_column(String(255), nullable=True)
    ollama_url: Mapped[str] = mapped_column(String(255), nullable=True, default="http://localhost:11434")

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="settings")
