from typing import Any

from sqlmodel import Session, select
from pathlib import Path
import tempfile
from app.models import (
    TacacsGroup,
    TacacsNG,
    Mavis,
    Host,
    TacacsGroup,
    TacacsUser,
    Profile,
    ProfileScript,
    ProfileScriptSet,
    Ruleset,
    RulesetScript,
    RulesetScriptSet,
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

    statement = select(TacacsGroup)
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

    # Begin profile
    tacacs_profiles_template = profile_generator(session=session)
    # Begin ruleset
    tacacs_rulesets_template = ruleset_generator(session=session)

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


def profile_generator(session: Session) -> str:
    profiles_db = session.exec(select(Profile)).all()
    profile_template = ""
    for profile_db in profiles_db:

        statement = select(ProfileScript).where(
            ProfileScript.profile_id == profile_db.id
        )
        script_in_profile = session.exec(statement).all()
        if script_in_profile == []:
            continue
        profilescript_template = ""
        for profilescript in script_in_profile:
            scriptset_in_profilescript = session.exec(
                select(ProfileScriptSet).where(
                    ProfileScriptSet.profilescript_id == profilescript.id
                )
            ).all()
            if scriptset_in_profilescript == []:
                continue
            profilescriptset_template = ""
            for profilescriptset in scriptset_in_profilescript:
                profilescriptset_info = profilescriptset.model_dump()
                profilescriptset_template += """set {key}={value}""".format(
                    key=profilescriptset_info["key"],
                    value=profilescriptset_info["value"],
                )

            profilescript_info = profilescript.model_dump()
            profilescript_template += """{condition} ({key}=={value}){{
            {profilescriptset_template}
            {action}
            }}""".format(
                condition=profilescript_info["condition"],
                key=profilescript_info["key"],
                value=profilescript_info["value"],
                profilescriptset_template=profilescriptset_template,
                action=profilescript_info["action"],
            )
        profile_template += """
    profile {profile_name} {{
        script {{
        {profilescript_template}
        {action}
        }}
    }}""".format(
            profile_name=profile_db.name,
            profilescript_template=profilescript_template,
            action=profile_db.action,
        )

    return profile_template


def ruleset_generator(session: Session) -> str:
    rulesets_db = session.exec(select(Ruleset)).all()
    ruleset_template = ""
    for ruleset_db in rulesets_db:
        statement = select(RulesetScript).where(
            RulesetScript.ruleset_id == ruleset_db.id
        )
        script_in_ruleset = session.exec(statement).all()

        if script_in_ruleset == []:
            continue
        rulesetscript_template = ""
        for rulesetscript in script_in_ruleset:
            scriptset_in_ruleset = session.exec(
                select(RulesetScriptSet).where(
                    RulesetScriptSet.rulesetscript_id == rulesetscript.id
                )
            ).all()
            if scriptset_in_ruleset == []:
                continue
            rulesetscriptset_template = ""
            for rulesetscriptset in scriptset_in_ruleset:
                rulesetscriptset_info = rulesetscriptset.model_dump()
                rulesetscriptset_template += """{key}={value}""".format(
                    key=rulesetscriptset_info["key"],
                    value=rulesetscriptset_info["value"],
                )

            rulesetscript_info = rulesetscript.model_dump()
            rulesetscript_template += """{condition} ({key}=={value}){{
                {rulesetscriptset_template}
                {action}
            }}
            """.format(
                condition=rulesetscript_info["condition"],
                key=rulesetscript_info["key"],
                value=rulesetscript_info["value"],
                rulesetscriptset_template=rulesetscriptset_template,
                action=rulesetscript_info["action"],
            )
        ruleset_template += """rule {rule_name} {{
            enabled=yes
            script {{
                {rulesetscript_template}
            {action}
            }}
        }}
        """.format(
            rule_name=ruleset_db.name,
            rulesetscript_template=rulesetscript_template,
            action=ruleset_db.action,
        )
    ruleset_all = """
    ruleset {{
        {ruleset_template}
    }}""".format(
        ruleset_template=ruleset_template
    )
    return ruleset_all
