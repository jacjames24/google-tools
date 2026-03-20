import socket
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    results = _orig_getaddrinfo(host, port, family, type, proto, flags)
    return [r for r in results if r[0] == socket.AF_INET]
socket.getaddrinfo = _ipv4_only

import os
import io
import json
import base64
from mcp.server.fastmcp import FastMCP, Image
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]
CREDENTIALS_PATH = r"C:\Users\jacja\Downloads\API Keys\client_secret_346514819391-k9oh1pm26nulrcan17qc9nlhtcq4ui4p.apps.googleusercontent.com.json"

ACCOUNTS = [
    {"name": "Personal", "token": r"C:\Users\jacja\Downloads\API Keys\token_personal_drive.json"},
    {"name": "Freelance", "token": r"C:\Users\jacja\Downloads\API Keys\token_freelance_drive.json"},
]

mcp = FastMCP("Google Drive Assistant")


def authenticate(token_path):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds


def _get_service(account_name: str):
    account = next((a for a in ACCOUNTS if a["name"].lower() == account_name.lower()), None)
    if not account:
        raise ValueError(f"Unknown account '{account_name}'. Available: {[a['name'] for a in ACCOUNTS]}")
    creds = authenticate(account["token"])
    return build("drive", "v3", credentials=creds)


def _get_sheets_service(account_name: str):
    account = next((a for a in ACCOUNTS if a["name"].lower() == account_name.lower()), None)
    if not account:
        raise ValueError(f"Unknown account '{account_name}'. Available: {[a['name'] for a in ACCOUNTS]}")
    creds = authenticate(account["token"])
    return build("sheets", "v4", credentials=creds)


@mcp.tool()
def list_drive_files(account: str = "Personal", folder_id: str = "root", max_results: int = 50) -> str:
    """
    List files and folders in a Google Drive folder.

    Args:
        account: Account name — "Personal" or "Freelance"
        folder_id: The folder ID to list (default: "root" for My Drive)
        max_results: Maximum number of files to return (default 50)
    """
    service = _get_service(account)
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query,
        pageSize=max_results,
        fields="files(id, name, mimeType, createdTime, modifiedTime, size)"
    ).execute()
    files = results.get("files", [])
    return json.dumps({"account": account, "folder_id": folder_id, "files": files, "total": len(files)}, indent=2)


@mcp.tool()
def search_drive_files(account: str = "Personal", keyword: str = "", mime_type: str = "", folder_id: str = "", max_results: int = 20) -> str:
    """
    Search for files in Google Drive.

    Args:
        account: Account name — "Personal" or "Freelance"
        keyword: Search keyword (matches file name)
        mime_type: Filter by MIME type (e.g. "image/jpeg", "image/png", "application/vnd.google-apps.folder")
        folder_id: Limit search to a specific folder ID (optional)
        max_results: Maximum number of results (default 20)
    """
    service = _get_service(account)

    query_parts = ["trashed = false"]
    if keyword:
        query_parts.append(f"name contains '{keyword}'")
    if mime_type:
        query_parts.append(f"mimeType = '{mime_type}'")
    if folder_id:
        query_parts.append(f"'{folder_id}' in parents")

    query = " and ".join(query_parts)
    results = service.files().list(
        q=query,
        pageSize=max_results,
        fields="files(id, name, mimeType, createdTime, modifiedTime, size, parents)"
    ).execute()
    files = results.get("files", [])
    return json.dumps({"account": account, "query": query, "files": files, "total": len(files)}, indent=2)


@mcp.tool()
def get_drive_image(account: str, file_id: str) -> Image:
    """
    Download an image from Google Drive and return it for visual analysis.

    Args:
        account: Account name — "Personal" or "Freelance"
        file_id: The file ID of the image to retrieve
    """
    service = _get_service(account)

    # Get file metadata
    file_meta = service.files().get(fileId=file_id, fields="name, mimeType").execute()
    mime_type = file_meta.get("mimeType", "image/jpeg")
    fmt = mime_type.split("/")[-1].lower()  # e.g. "jpeg", "png"
    if fmt == "jpg":
        fmt = "jpeg"

    # Download file content
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    return Image(data=buffer.getvalue(), format=fmt)


@mcp.tool()
def get_drive_folder_id(account: str = "Personal", folder_name: str = "") -> str:
    """
    Find a folder by name in Google Drive and return its ID.

    Args:
        account: Account name — "Personal" or "Freelance"
        folder_name: Name of the folder to search for
    """
    service = _get_service(account)
    query = f"mimeType = 'application/vnd.google-apps.folder' and name contains '{folder_name}' and trashed = false"
    results = service.files().list(
        q=query,
        fields="files(id, name, parents)"
    ).execute()
    folders = results.get("files", [])
    return json.dumps({"folders": folders, "total": len(folders)}, indent=2)


@mcp.tool()
def list_sheets(account: str, file_id: str) -> str:
    """
    List all sheet/tab names in a Google Spreadsheet.

    Args:
        account: Account name — "Personal" or "Freelance"
        file_id: The file ID of the Google Sheet
    """
    service = _get_sheets_service(account)
    meta = service.spreadsheets().get(spreadsheetId=file_id).execute()
    sheets = [s["properties"]["title"] for s in meta.get("sheets", [])]
    return json.dumps({"sheets": sheets}, indent=2)


@mcp.tool()
def read_sheet(account: str, file_id: str, sheet_name: str = "") -> str:
    """
    Read a Google Sheet and return its contents as a formatted table.

    Args:
        account: Account name — "Personal" or "Freelance"
        file_id: The file ID of the Google Sheet (from the URL)
        sheet_name: Optional specific sheet/tab name to read (default: first sheet)
    """
    service = _get_sheets_service(account)

    # If no sheet name given, look up the first sheet's name
    if not sheet_name:
        meta = service.spreadsheets().get(spreadsheetId=file_id).execute()
        sheet_name = meta["sheets"][0]["properties"]["title"]

    range_ = f"'{sheet_name}'"
    result = service.spreadsheets().values().get(
        spreadsheetId=file_id,
        range=range_,
        valueRenderOption="FORMATTED_VALUE",
    ).execute()

    rows = result.get("values", [])

    if not rows:
        return json.dumps({"error": "Sheet is empty"})

    # Normalize row widths
    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    # Format as markdown table
    headers = rows[0]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")

    import csv, io as _io
    buf = _io.StringIO()
    csv.writer(buf).writerows(rows)
    raw_csv = buf.getvalue()

    return json.dumps({
        "file_id": file_id,
        "sheet_name": sheet_name,
        "rows": len(rows) - 1,
        "columns": len(headers),
        "table": "\n".join(lines),
        "raw_csv": raw_csv,
    }, indent=2)


@mcp.tool()
def update_sheet(account: str, file_id: str, range: str, values: list) -> str:
    """
    Write values to a specific range in a Google Sheet.

    Args:
        account: Account name — "Personal" or "Freelance"
        file_id: The file ID of the Google Sheet
        range: A1 notation range to update (e.g. "Sheet1!A1", "A1:C3")
        values: 2D list of values to write (rows x columns)
    """
    service = _get_sheets_service(account)
    body = {"values": values}
    result = service.spreadsheets().values().update(
        spreadsheetId=file_id,
        range=range,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    return json.dumps({
        "updated_range": result.get("updatedRange"),
        "updated_rows": result.get("updatedRows"),
        "updated_columns": result.get("updatedColumns"),
        "updated_cells": result.get("updatedCells"),
    }, indent=2)


@mcp.tool()
def copy_row_format(account: str, file_id: str, source_row: int, target_row: int, sheet_name: str = "") -> str:
    """
    Copy the cell formatting from one row to another in a Google Sheet.
    Useful after appending a new row to match the style of existing rows.

    Args:
        account: Account name — "Personal" or "Freelance"
        file_id: The file ID of the Google Sheet
        source_row: The 1-indexed row number to copy formatting FROM
        target_row: The 1-indexed row number to apply formatting TO
        sheet_name: Sheet/tab name (default: first sheet)
    """
    service = _get_sheets_service(account)

    # Get sheet metadata to find the sheetId
    spreadsheet = service.spreadsheets().get(spreadsheetId=file_id).execute()
    sheets = spreadsheet.get("sheets", [])
    if sheet_name:
        sheet = next((s for s in sheets if s["properties"]["title"] == sheet_name), None)
        if not sheet:
            raise ValueError(f"Sheet '{sheet_name}' not found.")
    else:
        sheet = sheets[0]
    sheet_id = sheet["properties"]["sheetId"]
    col_count = sheet["properties"]["gridProperties"].get("columnCount", 26)

    result = service.spreadsheets().batchUpdate(
        spreadsheetId=file_id,
        body={
            "requests": [{
                "copyPaste": {
                    "source": {
                        "sheetId": sheet_id,
                        "startRowIndex": source_row - 1,
                        "endRowIndex": source_row,
                        "startColumnIndex": 0,
                        "endColumnIndex": col_count,
                    },
                    "destination": {
                        "sheetId": sheet_id,
                        "startRowIndex": target_row - 1,
                        "endRowIndex": target_row,
                        "startColumnIndex": 0,
                        "endColumnIndex": col_count,
                    },
                    "pasteType": "PASTE_FORMAT",
                    "pasteOrientation": "NORMAL",
                }
            }]
        }
    ).execute()

    return json.dumps({
        "source_row": source_row,
        "target_row": target_row,
        "replies": result.get("replies", []),
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
