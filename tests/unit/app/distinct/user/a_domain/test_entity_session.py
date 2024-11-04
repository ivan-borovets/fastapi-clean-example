from datetime import datetime, timedelta
from uuid import UUID

from app.distinct.user.a_domain.entity_session import Session
from app.distinct.user.a_domain.vo_session import SessionId, SessionExpiration
from app.distinct.user.a_domain.vo_user import UserId


def test_session_init():
    session_id = "session1234"
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    expiration = datetime.now() + timedelta(days=1)

    vo_session_id = SessionId(session_id)
    vo_user_id = UserId(user_id)
    vo_expiration = SessionExpiration(expiration)

    direct_session = Session(
        id_=vo_session_id, user_id=vo_user_id, expiration=vo_expiration
    )
    indirect_session = Session.create(
        session_id=session_id, user_id=user_id, expiration=expiration
    )

    assert isinstance(indirect_session, Session)
    assert direct_session.id_ == vo_session_id == indirect_session.id_
    assert direct_session.user_id == vo_user_id == indirect_session.user_id
    assert direct_session.expiration == vo_expiration == indirect_session.expiration
    assert direct_session == indirect_session


def test_extend_session(sample_session):
    new_expiration: datetime = datetime.now() + timedelta(days=5)
    sample_session.extend(new_expiration)
    assert sample_session.expiration.value == new_expiration
