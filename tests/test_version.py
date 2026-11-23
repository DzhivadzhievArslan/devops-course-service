from app.model import model_version


def test_version_ignores_line_endings(tmp_path):
    # Те же данные с переносами LF и CRLF должны давать одну версию модели.
    rows = "text,label\nГде мой заказ?,delivery\nЗабыл пароль,account\n"
    lf = tmp_path / "lf.csv"
    crlf = tmp_path / "crlf.csv"
    lf.write_bytes(rows.encode("utf-8"))
    crlf.write_bytes(rows.replace("\n", "\r\n").encode("utf-8"))
    assert model_version(lf) == model_version(crlf)


def test_version_changes_with_data(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("text,label\nГде мой заказ?,delivery\n", encoding="utf-8")
    b.write_text("text,label\nГде мой заказ?,refund\n", encoding="utf-8")
    assert model_version(a) != model_version(b)
