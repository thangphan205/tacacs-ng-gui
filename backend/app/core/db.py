from sqlmodel import Session, create_engine, select

from app.crud import users
from app.core.config import settings
from app.models import User, UserCreate, TacacsNG, TacacsNGCreate, Mavis, MavisCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = users.create_user(session=session, user_create=user_in)

    tacacs_settings = session.exec(select(TacacsNG)).first()
    if not tacacs_settings:
        tacacs_in = TacacsNGCreate(
            ipv4_enabled=settings.IPV4_ENABLED,
            ipv4_address=settings.IPV4_ADDRESS,
            ipv4_port=settings.IPV4_PORT,
            ipv6_enabled=settings.IPV6_ENABLED,
            ipv6_address=settings.IPV6_ADDRESS,
            ipv6_port=settings.IPV6_PORT,
            instances_min=settings.INSTANCES_MIN,
            instances_max=settings.INSTANCES_MAX,
            background=settings.BACKGROUND,
            access_log_destination=settings.ACCESS_LOG_DESTINATION,
            accounting_logfile_destination=settings.ACCOUNTING_LOG_DESTINATION,
            authentication_logfile_destination=settings.AUTHENTICATION_LOG_DESTINATION,
            login_backend=settings.LOGIN_BACKEND,
            user_backend=settings.USER_BACKEND,
            pap_backend=settings.PAP_BACKEND,
        )
        tacacs_settings = TacacsNG.model_validate(tacacs_in)
        session.add(tacacs_settings)
        session.commit()
        session.refresh(tacacs_settings)

    mavis = session.exec(select(Mavis)).first()
    if not mavis:
        mavis_in = MavisCreate(
            ldap_server_type=settings.LDAP_SERVER_TYPE,
            ldap_host=settings.LDAP_HOSTS,
            ldap_base=settings.LDAP_BASE,
            ldap_user=settings.LDAP_USER,
            ldap_passwd=settings.LDAP_PASSWD,
            require_tacacs_group_prefix=settings.REQUIRE_TACACS_GROUP_PREFIX,
            tacacs_group_prefix=settings.TACACS_GROUP_PREFIX,
            ldap_filter=settings.LDAP_FILTER,
        )
        mavis_settings = Mavis.model_validate(mavis_in)
        session.add(mavis_settings)
        session.commit()
        session.refresh(mavis_settings)
