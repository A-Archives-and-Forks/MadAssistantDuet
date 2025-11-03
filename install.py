from pathlib import Path

import shutil
import sys

try:
    import jsonc
except ModuleNotFoundError as e:
    raise ImportError(
        "Missing dependency 'json-with-comments' (imported as 'jsonc').\n"
        f"Install it with:\n  {sys.executable} -m pip install json-with-comments\n"
        "Or add it to your project's requirements."
    ) from e

from configure import configure_ocr_model


working_dir = Path(__file__).parent
install_path = working_dir / Path("install")
version = len(sys.argv) > 1 and sys.argv[1] or "v0.0.1"


def install_deps():
    if not (working_dir / "deps" / "bin").exists():
        print("Please download the MaaFramework to \"deps\" first.")
        print("请先下载 MaaFramework 到 \"deps\"。")
        sys.exit(1)

    shutil.copytree(
        working_dir / "deps" / "bin",
        install_path,
        ignore=shutil.ignore_patterns(
            "*MaaDbgControlUnit*",
            "*MaaThriftControlUnit*",
            "*MaaRpc*",
            "*MaaHttp*",
        ),
        dirs_exist_ok=True,
    )
    shutil.copytree(
        working_dir / "deps" / "share" / "MaaAgentBinary",
        install_path / "MaaAgentBinary",
        dirs_exist_ok=True,
    )


def install_resource():

    configure_ocr_model()

    shutil.copytree(
        working_dir / "assets" / "resource",
        install_path / "resource",
        dirs_exist_ok=True,
    )
    shutil.copy2(
        working_dir / "assets" / "interface.json",
        install_path,
    )

    with open(install_path / "interface.json", "r", encoding="utf-8") as f:
        interface = jsonc.load(f)

    interface["version"] = version

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        jsonc.dump(interface, f, ensure_ascii=False, indent=4)


def install_chores():
    shutil.copy2(
        working_dir / "README.md",
        install_path,
    )
    shutil.copy2(
        working_dir / "LICENSE",
        install_path,
    )
    
    # 检测目标平台并复制对应的 requirements 文件
    # 通过检查 deps/bin 中的文件来判断平台
    is_windows = False
    if (working_dir / "deps" / "bin").exists():
        # Windows 平台会有 .dll 文件
        dll_files = list((working_dir / "deps" / "bin").glob("*.dll"))
        is_windows = len(dll_files) > 0
    
    if is_windows:
        # Windows 平台使用 requirements-windows.txt (包含 pywin32)
        if (working_dir / "requirements-windows.txt").exists():
            shutil.copy2(
                working_dir / "requirements-windows.txt",
                install_path / "requirements.txt",
            )
        else:
            # 兜底：如果文件不存在，使用原始的 requirements.txt
            shutil.copy2(
                working_dir / "requirements.txt",
                install_path,
            )
    else:
        # 非 Windows 平台使用 requirements-base.txt (不含 pywin32)
        if (working_dir / "requirements-base.txt").exists():
            shutil.copy2(
                working_dir / "requirements-base.txt",
                install_path / "requirements.txt",
            )
        else:
            # 兜底：如果文件不存在，使用原始的 requirements.txt
            shutil.copy2(
                working_dir / "requirements.txt",
                install_path,
            )

def install_agent():
    shutil.copytree(
        working_dir / "agent",
        install_path / "agent",
        dirs_exist_ok=True,
    )

if __name__ == "__main__":
    install_deps()
    install_resource()
    install_chores()
    install_agent()

    print(f"Install to {install_path} successfully.")