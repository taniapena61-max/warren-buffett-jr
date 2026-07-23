"""Tests del almacén de historial diario (Schwab no guarda el pasado)."""

from datetime import date

from wbj.history import leer, registrar, registrar_quote


def test_registra_y_lee(tmp_path):
    assert registrar("IREN", {"precio": 41.29, "iv": 130.5}, tmp_path,
                     cuando=date(2026, 7, 21))
    filas = leer("IREN", tmp_path)
    assert len(filas) == 1
    assert filas[0]["fecha"] == "2026-07-21"
    assert filas[0]["precio"] == "41.29"


def test_upsert_una_fila_por_dia(tmp_path):
    # varias consultas el mismo dia -> UNA fila, la ultima gana
    registrar("IREN", {"precio": 41.0}, tmp_path, cuando=date(2026, 7, 21))
    registrar("IREN", {"precio": 42.5}, tmp_path, cuando=date(2026, 7, 21))
    filas = leer("IREN", tmp_path)
    assert len(filas) == 1
    assert filas[0]["precio"] == "42.5"


def test_dias_distintos_acumulan_ordenados(tmp_path):
    registrar("IREN", {"precio": 42.5}, tmp_path, cuando=date(2026, 7, 22))
    registrar("IREN", {"precio": 41.0}, tmp_path, cuando=date(2026, 7, 21))
    filas = leer("IREN", tmp_path)
    assert [f["fecha"] for f in filas] == ["2026-07-21", "2026-07-22"]


def test_simbolo_opcion_con_espacios(tmp_path):
    sym = "IREN  260814P00047000"
    assert registrar_quote(sym, {"mark": 9.0, "delta": -0.6, "volatility": 123.6},
                           tmp_path)
    filas = leer(sym, tmp_path)
    assert filas and filas[0]["iv"] == "123.6"


def test_acepta_repo_root_o_carpeta_historial(tmp_path):
    # pasar repo_root o repo_root/historial debe apuntar al MISMO sitio
    registrar("AAA", {"p": 1.0}, tmp_path, cuando=date(2026, 1, 1))
    registrar("AAA", {"p": 2.0}, tmp_path / "historial", cuando=date(2026, 1, 2))
    filas = leer("AAA", tmp_path / "historial")
    assert len(filas) == 2  # ambas escrituras cayeron en la misma carpeta


def test_quote_sin_campos_utiles_no_rompe(tmp_path):
    assert registrar_quote("XXX", {"algoRaro": "sinValor"}, tmp_path) is False
