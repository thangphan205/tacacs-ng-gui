from typing import Any

from sqlmodel import Session, select
from pathlib import Path
import tempfile
from app.models import (
    TacacsGroupUser,
    TacacsGroupUserCreate,
    TacacsGroupUserUpdate,
    TacacsNG,
    Mavis,
    Host,
    TacacsGroupUser,
    TacacsUser,
    Profile,
    ProfileScript,
    ProfileScriptSet,
    Ruleset,
    RulesetScript,
)
import os

# Base path cho volume được mount bên trong container FastAPI:
# Path này tương ứng với 'tacacs_data_volume' được mount vào /app/tacacs_config_and_logs
SHARED_BASE_PATH = "/app/tacacs_config_and_logs"

# Đường dẫn tuyệt đối đến tệp cấu hình
CONFIG_FILE_PATH = os.path.join(SHARED_BASE_PATH, "etc", "tac_plus-ng.cfg")

# Đường dẫn tuyệt đối đến tệp nhật ký (log file)
LOG_FILE_PATH = os.path.join(SHARED_BASE_PATH, "log", "auth.log")

# Đường dẫn tuyệt đối đến tệp kích hoạt reload (monitor script sẽ theo dõi tệp này)
RELOAD_TRIGGER_PATH = os.path.join(SHARED_BASE_PATH, "restart_trigger.txt")


def generate_tacacs_ng_config(*, session: Session) -> Any:
    """
    Hàm này tạo và trả về nội dung cấu hình TACACS+ mặc định dưới dạng chuỗi.
    Bạn có thể tùy chỉnh cấu hình mặc định theo yêu cầu của mình.
    """

    statement = select(TacacsNG).limit(1)
    tacacs_ng_basic = session.exec(statement).first()
    tacacs_ng_info = tacacs_ng_basic.model_dump()

    statement = select(Mavis).limit(1)
    mavis_basic = session.exec(statement).first()
    mavis_info = mavis_basic.model_dump()

    statement = select(Host).limit(1)
    host_basic = session.exec(statement).all()

    config_file_template = """#!../../../sbin/tac_plus-ng
id = spawnd {{
    listen = {{
        address = {addr}
        port = {port}
    }}
    spawn = {{
        instances min = {inst_min}
        instances max = {inst_max}
    }}
    background = {bg}
}}
id = tac_plus-ng {{
    log accesslog {{ destination = {accesslog} }}
    log accountinglog {{ destination = {accountinglog} }}
    log authenticationlog {{ destination = {authenticationlog} }}
    access log = accesslog
    accounting log = accountinglog
    authentication log = authenticationlog
    mavis module = external {{
        # Set environment variables for LDAP connection
        setenv LDAP_SERVER_TYPE = "{ldap_server_type}"
        setenv LDAP_HOSTS = "{ldap_hosts}"
        setenv LDAP_BASE = "{ldap_base}"
        setenv LDAP_USER = "{ldap_user}"
        setenv LDAP_PASSWD = "{ldap_passwd}"
        setenv REQUIRE_TACACS_GROUP_PREFIX = 0
        setenv LDAP_FILTER = "{ldap_filter}"
        setenv TACACS_GROUP_PREFIX = "tacacs_"

        exec = /usr/local/lib/mavis/mavis_tacplus-ng_ldap.pl
    }}""".format(
        addr=tacacs_ng_info["ipv4_address"],
        port=tacacs_ng_info["ipv4_port"],
        inst_min=tacacs_ng_info["instances_min"],
        inst_max=tacacs_ng_info["instances_max"],
        bg=str(tacacs_ng_info["background"]).lower(),
        accesslog=tacacs_ng_info["access_logfile_destination"],
        accountinglog=tacacs_ng_info["accounting_logfile_destination"],
        authenticationlog=tacacs_ng_info["authentication_logfile_destination"],
        ldap_server_type=mavis_info["ldap_server_type"],
        ldap_hosts=mavis_info["ldap_hosts"],
        ldap_base=mavis_info["ldap_base"],
        ldap_user=mavis_info["ldap_user"],
        ldap_passwd=mavis_info["ldap_passwd"],
        ldap_filter=mavis_info["ldap_filter"],
    )
    hosts_template = ""
    for host in host_basic:
        host_info = host.model_dump()
        hosts_template += """
    host = {host_name} {{
        address = {host_address}
        key = "{host_key}"
    }}""".format(
            host_name=host_info["name"],
            host_address=host_info["ipv4_address"],
            host_key=host_info["secret_key"],
        )

    statement = select(TacacsGroupUser)
    tacacs_group_basic = session.exec(statement).all()
    tacacs_groups_template = ""
    for tacacs_group in tacacs_group_basic:
        tacacs_group_info = tacacs_group.model_dump()
        tacacs_groups_template += """
    group = {group_name}""".format(
            group_name=tacacs_group_info["group_name"]
        )

    statement = select(TacacsUser)
    tacacs_users_basic = session.exec(statement).all()
    tacacs_users_template = ""
    for tacacs_user in tacacs_users_basic:
        tacacs_user_info = tacacs_user.model_dump()
        if tacacs_user_info["password_type"] == "mavis":
            tacacs_users_template += """
    user {username} {{
        password login = mavis
        member = {member}
    }}""".format(
                username=tacacs_user_info["username"],
                member=tacacs_user_info["member"],
            )
        else:

            tacacs_users_template += """
    user {username} {{
        password login = {mavis_type} {mavis_password}
        member = {member}
    }}""".format(
                username=tacacs_user_info["username"],
                mavis_type=tacacs_user_info["password_type"],
                mavis_password=tacacs_user_info["password"],
                member=tacacs_user_info["member"],
            )

    statement = select(Profile)
    tacacs_profiles_basic = session.exec(statement).all()
    tacacs_profiles_template = ""
    for tacacs_profile in tacacs_profiles_basic:
        tacacs_profile_info = tacacs_profile.model_dump()
        statement_script = select(ProfileScript).where(
            ProfileScript.profile_id == tacacs_profile_info["id"]
        )
        tacacs_profilescripts_basic = session.exec(statement_script).all()

        tacacs_profilescript_template = ""
        for tacacs_profilescript in tacacs_profilescripts_basic:
            tacacs_profilescript_info = tacacs_profilescript.model_dump()
            statement_scriptset = select(ProfileScriptSet).where(
                tacacs_profilescript_info["profile_id"] == tacacs_profile_info["id"]
            )
            tacacs_profilescriptsets_basic = session.exec(statement_scriptset).all()

            tacacs_profilescriptset_template = ""
            for tacacs_profilescriptset in tacacs_profilescriptsets_basic:
                tacacs_profilescriptset_info = tacacs_profilescriptset.model_dump()
                tacacs_profilescriptset_template += """
                set {script_key} = {script_value}""".format(
                    script_key=tacacs_profilescriptset_info["key"],
                    script_value=tacacs_profilescriptset_info["value"],
                )
            tacacs_profilescript_template += """
            if ( service == {value}) {{
                {script_set}
                {action}
            }}""".format(
                key=tacacs_profilescript_info["key"],
                value=tacacs_profilescript_info["value"],
                script_set=tacacs_profilescriptset_template,
                action=tacacs_profilescript_info["action"],
            )

        tacacs_profiles_template += """
    profile {profile_name} {{
        script {{
        {profile_scripts}
        {action}
        }}
    }}""".format(
            profile_name=tacacs_profile_info["name"],
            profile_scripts=tacacs_profilescript_template,
            action=tacacs_profile_info["action"],
        )

    # Begin ruleset
    statement = select(Ruleset)
    tacacs_rulesets_basic = session.exec(statement).all()
    tacacs_rulesets_template = ""
    for ruleset in tacacs_rulesets_basic:
        ruleset_info = ruleset.model_dump()
        statement_rulescript = select(RulesetScript).where(
            RulesetScript.ruleset_id == ruleset_info["id"]
        )
        tacacs_rulescripts_basic = session.exec(statement_rulescript).all()

        tacacs_rulescript_template = ""
        for rulescript in tacacs_rulescripts_basic:
            rulescript_info = rulescript.model_dump()
            tacacs_rulescript_template += """
                if ( group == {group_name} ) {{
                    profile = {profile_name}
                    {action}
                }}""".format(
                group_name=rulescript_info["group_name"],
                profile_name=rulescript_info["profile_name"],
                action=rulescript_info["action"],
            )

        tacacs_rulesets_template += """
    ruleset {{
        rule {ruleset_name} {{
            enabled = yes
            script {{
            {ruleset_scripts}
            deny
            }}
        }}
    }}""".format(
            ruleset_name=ruleset_info["name"],
            ruleset_scripts=tacacs_rulescript_template,
        )
    # End ruleset

    config_file_template += (
        hosts_template
        + tacacs_groups_template
        + tacacs_users_template
        + tacacs_profiles_template
        + tacacs_rulesets_template
        + "\n}\n"
    )

    config_path = Path.cwd() / "tacacs-ng.conf"
    try:
        config_path.write_text(config_file_template, encoding="utf-8")
    except OSError:
        tf = tempfile.NamedTemporaryFile(
            delete=False, suffix=".conf", prefix="tacacs-ng-"
        )
        tf.write(config_file_template.encode("utf-8"))
        tf.close()
        config_path = Path(tf.name)

    return config_file_template


def get_group_by_group_name(
    *, session: Session, group_name: str
) -> TacacsGroupUser | None:
    statement = select(TacacsGroupUser).where(TacacsGroupUser.group_name == group_name)
    session_user = session.exec(statement).first()
    return session_user


def create_group(
    *, session: Session, user_create: TacacsGroupUserCreate
) -> TacacsGroupUser:
    db_obj = TacacsGroupUser.model_validate(user_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_group(
    *, session: Session, db_user: TacacsGroupUser, group_in: TacacsGroupUserUpdate
) -> Any:
    user_data = group_in.model_dump(exclude_unset=True)
    extra_data = {}
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
