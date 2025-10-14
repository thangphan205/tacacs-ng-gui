import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# --- TACACS+ Configuration Tables ---


class SpawndBase(SQLModel):
    ipv4_enabled: bool = Field(default=True)
    ipv4_address: Optional[str] = None  # None means bind to all interfaces
    ipv4_port: int = Field(default=49)
    ipv6_enabled: bool = Field(default=False)
    ipv6_address: Optional[str] = None  # None means bind to all interfaces
    ipv6_port: int = Field(default=49)
    instances_min: int = Field(default=1)
    instances_max: int = Field(default=10)
    backgroudd: bool = Field(default=False)


# Database model, database table inferred from class name
class Spawnd(SpawndBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API, id is always required
class SpawndPublic(SpawndBase):
    id: uuid.UUID


class SpawndsPublic(SQLModel):
    data: list[SpawndPublic]
    count: int


class TacacsNGBase(SQLModel):
    access_logfile: str = Field(default="/var/log/tac_plus/%Y/access-%m-%d-%Y.txt")
    accounting_logfile: str = Field(
        default="/var/log/tac_plus/%Y/accounting-%m-%d-%Y.txt"
    )
    authentication_logfile: str = Field(
        default="/var/log/tac_plus/%Y/authentication-%m-%d-%Y.txt"
    )
    login_backend: str = Field(default="mavis")
    user_backend: str = Field(default="mavis")
    pap_backend: str = Field(default="mavis")


# Database model, database table inferred from class name
class TacacsNG(TacacsNGBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API, id is always required
class TacacsNGPublic(TacacsNGBase):
    id: uuid.UUID


class TacacsNGsPublic(SQLModel):
    data: list[TacacsNGPublic]
    count: int


class MavisBase(SQLModel):
    ldap_server_type: str = Field(default="openldap")  # or 'active_directory'
    ldap_hosts: str = Field(default="ldaps://ldap-server")
    ldap_base: str = Field(default="dc=example,dc=com")
    ldap_user: str = Field(default="cn=admin,dc=example,dc=com")
    ldap_password: str = Field(default="admin_password")
    ldap_filter: str = Field(default="(objectClass=person)")
    ldap_timeout: int = Field(default=5)
    ldap_tls: bool = Field(default=True)
    ldap_tls_require_cert: str = Field(default="demand")  # or 'allow', 'never'
    ldap_tls_cacertfile: Optional[str] = Field(
        default="/etc/ssl/certs/ca-certificates.crt"
    )
    ldap_tls_cacertdir: Optional[str] = None
    ldap_tls_certfile: Optional[str] = None
    ldap_tls_keyfile: Optional[str] = None
    group_attribute: str = Field(default="memberOf")
    group_attribute_is_dn: bool = Field(default=True)
    group_name_attribute: str = Field(default="cn")
    user_name_attribute: str = Field(default="uid")
    user_fullname_attribute: str = Field(default="cn")
    user_email_attribute: str = Field(default="mail")
    user_password_attribute: str = Field(default="userPassword")
    posix_user_attribute: str = Field(default="uidNumber")
    posix_group_attribute: str = Field(default="gidNumber")
    posix_homedir_attribute: str = Field(default="homeDirectory")
    posix_shell_attribute: str = Field(default="loginShell")
    ad_domain: Optional[str] = None
    ad_use_sasl: bool = Field(default=False)
    ad_sasl_user: Optional[str] = None
    ad_sasl_realm: Optional[str] = None
    ad_sasl_password: Optional[str] = None
    ad_use_kerberos: bool = Field(default=False)
    ad_kerberos_keytab: Optional[str] = None
    ad_kerberos_realm: Optional[str] = None
    ad_kerberos_kdc: Optional[str] = None
    cache_enabled: bool = Field(default=True)
    cache_ttl: int = Field(default=300)
    cache_negative_ttl: int = Field(default=60)
    default_profile: str = Field(default="default_profile")
    superuser_group: str = Field(default="tacacs_super_user")
    debug: bool = Field(default=False)


# Database model, database table inferred from class name
class Mavis(MavisBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API, id is always required
class MavisPublic(MavisBase):
    id: uuid.UUID


class MavisesPublic(SQLModel):
    data: list[MavisPublic]
    count: int


class HostBase(SQLModel):
    hostname: str = Field(index=True, max_length=255)
    ipv4_address: Optional[str] = None
    ipv6_address: Optional[str] = None
    secret_key: str = Field(max_length=255)


# Database model, database table inferred from class name
class Host(HostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API, id is always required
class HostPublic(HostBase):
    id: uuid.UUID


class HostsPublic(SQLModel):
    data: list[HostPublic]
    count: int


class TacacsGroupUserBase(SQLModel):
    group_name: str = Field(index=True, max_length=255)
    description: Optional[str] = None


class TacacsGroupUserCreate(TacacsGroupUserBase):
    pass


class TacacsGroupUserUpdate(TacacsGroupUserBase):
    pass


# Database model, database table inferred from class name
class TacacsGroupUser(TacacsGroupUserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API, id is always required
class TacacsGroupUserPublic(TacacsGroupUserBase):
    id: uuid.UUID


class TacacsGroupUsersPublic(SQLModel):
    data: list[TacacsGroupUserPublic]
    count: int


# -- Tacacs User Table ---
class TacacsUserBase(SQLModel):
    username: str = Field(index=True, unique=True, max_length=255)
    password_type: str = Field(index=True, max_length=255)
    member: str = Field(index=True, max_length=255)
    description: Optional[str] = None


class TacacsUserCreate(TacacsUserBase):
    password: str | None = Field(default=None, min_length=8, max_length=40)


class TacacsUserUpdate(TacacsUserBase):
    password: str | None = Field(default=None, min_length=8, max_length=40)


# Database model, database table inferred from class name
class TacacsUser(TacacsUserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API, id is always required
class TacacsUserPublic(TacacsUserBase):
    id: uuid.UUID


class TacacsUsersPublic(SQLModel):
    data: list[TacacsUserPublic]
    count: int


# -- Service Table ---
class ServiceBase(SQLModel):
    name: str = Field(index=True, max_length=255)
    description: Optional[str] = None


# Database model, database table inferred from class name
class Service(ServiceBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API, id is always required
class ServicePublic(ServiceBase):
    id: uuid.UUID


class ServicesPublic(SQLModel):
    data: list[ServicePublic]
    count: int


# -- Begin Profile and Profile Script Tables --
# -- Profile Table ---
class ProfileBase(SQLModel):
    condition: str = Field(index=True, max_length=255)
    key: str = Field(index=True, max_length=255)
    value: str = Field(index=True, max_length=255)
    action: str = Field(index=True, max_length=255)
    description: Optional[str] = None


# Database model, database table inferred from class name
class Profile(ProfileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    profile_scripts: List["ProfileScript"] = Relationship(
        back_populates="profile", cascade_delete=True
    )


# Properties to return via API, id is always required
class ProfilePublic(ProfileBase):
    id: uuid.UUID


class ProfilesPublic(SQLModel):
    data: list[ProfilePublic]
    count: int


# -- Profile Script  Table ---
class ProfileScriptBase(SQLModel):
    condition: str = Field(index=True, max_length=255)
    key: str = Field(index=True, max_length=255)
    value: str = Field(index=True, max_length=255)
    action: str = Field(index=True, max_length=255)
    description: Optional[str] = None


# Database model, database table inferred from class name
class ProfileScript(ProfileScriptBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    profile_id: uuid.UUID = Field(
        foreign_key="profile.id", nullable=False, ondelete="CASCADE"
    )
    profile: Profile | None = Relationship(back_populates="profile_scripts")


# Properties to return via API, id is always required
class ProfileScriptPublic(ProfileScriptBase):
    id: uuid.UUID


class ProfileScriptsPublic(SQLModel):
    data: list[ProfileScriptPublic]
    count: int


# -- Profile Script Set Table ---
class ProfileScriptSetBase(SQLModel):
    key: str = Field(index=True, max_length=255)
    value: str
    description: Optional[str] = None


# Database model, database table inferred from class name
class ProfileScriptSet(ProfileScriptSetBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API, id is always required
class ProfileScriptSetPublic(ProfileScriptSetBase):
    id: uuid.UUID


class ProfileScriptSetsPublic(SQLModel):
    data: list[ProfileScriptSetPublic]
    count: int


# -- End Profile and Profile Script Tables --


# -- Begin Ruleset Table --
# -- Profile Table ---
class RulesetBase(SQLModel):
    name: str = Field(index=True, max_length=255)
    enabled: bool = Field(default=True)
    action: str = Field(index=True, max_length=255)
    description: Optional[str] = None


# Database model, database table inferred from class name
class RuleSet(RulesetBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ruleset_scripts: List["RuleSetScript"] = Relationship(
        back_populates="ruleset", cascade_delete=True
    )


# Properties to return via API, id is always required
class RuleSetPublic(RulesetBase):
    id: uuid.UUID


class RulesetsPublic(SQLModel):
    data: list[RuleSetPublic]
    count: int


# -- Ruleset Script  Table ---
class RulesetScriptBase(SQLModel):
    condition: str = Field(index=True, max_length=255)
    group_name: str = Field(index=True, max_length=255)
    profile_name: str = Field(index=True, max_length=255)
    action: str = Field(index=True, max_length=255)
    description: Optional[str] = None


# Database model, database table inferred from class name
class RuleSetScript(RulesetScriptBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ruleset_id: uuid.UUID = Field(
        foreign_key="ruleset.id", nullable=False, ondelete="CASCADE"
    )
    ruleset: RuleSet | None = Relationship(back_populates="ruleset_scripts")


# Properties to return via API, id is always required
class RuleSetScriptPublic(RulesetScriptBase):
    id: uuid.UUID


class RuleSetScriptsPublic(SQLModel):
    data: list[RuleSetScriptPublic]
    count: int


# --- End of TACACS+ Configuration Tables ---
