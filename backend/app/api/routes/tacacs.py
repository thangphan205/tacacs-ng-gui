from fastapi import APIRouter, HTTPException, Body
import os
import time
from app.crud.tacacs_config import generate_tacacs_ng_config
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)

# router = APIRouter()
router = APIRouter(prefix="/tacacs", tags=["tacacs"])
# --- Định nghĩa đường dẫn chia sẻ (MUST match Docker Compose volume mounts) ---

# Base path cho volume được mount bên trong container FastAPI:
# Path này tương ứng với 'tacacs_data_volume' được mount vào /app/tacacs_config_and_logs
SHARED_BASE_PATH = "/app/tacacs_config_and_logs"

# Đường dẫn tuyệt đối đến tệp cấu hình
CONFIG_FILE_PATH = os.path.join(SHARED_BASE_PATH, "etc", "tac_plus-ng.cfg")

# Đường dẫn tuyệt đối đến tệp nhật ký (log file)
LOG_FILE_PATH = os.path.join(SHARED_BASE_PATH, "log", "auth.log")

# Đường dẫn tuyệt đối đến tệp kích hoạt reload (monitor script sẽ theo dõi tệp này)
RELOAD_TRIGGER_PATH = os.path.join(SHARED_BASE_PATH, "restart_trigger.txt")


@router.get("/config")
def get_config():
    """Đọc và trả về nội dung tệp cấu hình TACACS+ hiện tại."""
    try:
        if not os.path.exists(CONFIG_FILE_PATH):
            # Kiểm tra xem thư mục cấu hình đã tồn tại chưa (phòng trường hợp chạy lần đầu)
            if not os.path.exists(os.path.dirname(CONFIG_FILE_PATH)):
                os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)

            # Trả về lỗi nếu file chưa được tạo bởi script khởi động
            raise HTTPException(
                status_code=404,
                detail="Configuration file not found. Ensure tacacs_ng service is running to create the default config.",
            )

        with open(CONFIG_FILE_PATH, "r") as f:
            content = f.read()

        return {"filename": "tac_plus-ng.cfg", "content": content}

    except FileNotFoundError:
        # Lỗi này chỉ xảy ra nếu file bị xóa sau khi kiểm tra os.path.exists
        raise HTTPException(
            status_code=500, detail="Unexpected error: Configuration file disappeared."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading config: {e}")


@router.post("/config/save")
def save_config(
    session: SessionDep,
):
    """
    Ghi nội dung mới vào tệp cấu hình TACACS+ và tự động kích hoạt
    quá trình reload cấu hình trong container tacacs_ng thông qua SIGHUP.
    """
    tacacs_config = generate_tacacs_ng_config(session=session)
    # with open("tacacs_config.cfg", "w") as f:
    #     f.write(tacacs_config)
    # f.close()
    # return {
    #     "message": "Configuration saved successfully.",
    # }
    # 1. Lưu cấu hình mới
    try:
        # Ghi nội dung mới, ghi đè tệp cũ
        with open(CONFIG_FILE_PATH, "w") as f:
            f.write(tacacs_config)
    except Exception as e:
        # Do volume được chmod 777 nên lỗi này thường là lỗi I/O hệ thống
        raise HTTPException(
            status_code=500,
            detail=f"Error writing config: {e}. Check volume permissions.",
        )

    # 2. Kích hoạt tự động tải lại (Automatic Reload Trigger)
    try:
        # Đảm bảo tệp trigger tồn tại (dù script khởi động đã tạo)
        os.makedirs(os.path.dirname(RELOAD_TRIGGER_PATH), exist_ok=True)

        # Cập nhật timestamp (thao tác 'touch') của tệp trigger.
        # Script monitor trong tacacs_ng container sẽ phát hiện sự thay đổi này.
        os.utime(RELOAD_TRIGGER_PATH, None)

    except Exception as e:
        # Xử lý nếu việc chạm tệp trigger thất bại
        print(f"Warning: Failed to touch reload trigger file: {e}")
        return {
            "message": "Configuration saved successfully, but automatic reload trigger failed.",
            "action_required": "The TACACS+ service may not have reloaded. Check tacacs_ng container logs.",
        }

    # 3. Trả về thành công
    return {
        "message": "Configuration saved successfully and automatic reload triggered.",
        "action_required": "The TACACS+ service should reload configuration within 5 seconds (due to monitor script interval).",
    }


@router.get("/logs/auth")
def get_auth_logs(lines: int = 20):
    """Đọc N dòng cuối cùng của tệp nhật ký xác thực TACACS+."""
    if lines <= 0:
        raise HTTPException(
            status_code=400, detail="The 'lines' parameter must be a positive integer."
        )

    try:
        if not os.path.exists(LOG_FILE_PATH):
            return {
                "logs": [],
                "message": "Authentication log file does not exist yet. Run some TACACS+ tests to generate logs.",
            }

        with open(LOG_FILE_PATH, "r") as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]

        return {"filename": "auth.log", "logs": last_lines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {e}")
