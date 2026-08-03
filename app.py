"""Tkinter desktop interface for SSE XML Explorer."""

from __future__ import annotations

import ipaddress
import json
import os
from pathlib import Path
import re
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk
from dotenv import load_dotenv

from network_reader import AuthenticationError, consultar_knr
from utils.errors import CaminhoNaoEncontradoError, KNRNaoEncontradoError

load_dotenv()

APP_VERSION = "2.1"
PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PROJECT_ROOT / "config"
LOCAL_STATIONS = CONFIG_DIR / "stations.local.json"
EXAMPLE_STATIONS = CONFIG_DIR / "stations.example.json"
KNR_PATTERN = re.compile(r"^\d{8}$")


def load_stations() -> dict[str, str]:
    source = LOCAL_STATIONS if LOCAL_STATIONS.is_file() else EXAMPLE_STATIONS
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Não foi possível carregar {source.name}.") from exc
    if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
        raise RuntimeError(f"Formato inválido em {source.name}.")
    return data


def validar_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def validar_knr(value: str) -> bool:
    """A KNR is exactly eight ASCII digits in every application layer."""
    return KNR_PATTERN.fullmatch(value) is not None


class SSEExplorerApp:
    def __init__(self, root: ttk.Window) -> None:
        self.root = root
        self.stations = load_stations()
        self.xml_atual: str | None = None
        self.status_var = tk.StringVar(value=f"Status: Pronto | Versão {APP_VERSION}")
        self.filter_var = tk.StringVar()
        self._build_ui()
        self._populate_stations()

    def _build_ui(self) -> None:
        self.root.title("SSE XML Explorer")
        self.root.geometry("1200x850")
        self.root.minsize(1000, 700)

        ttk.Label(self.root, text="SSE XML EXPLORER", font=("Segoe UI", 24, "bold")).pack(pady=(15, 2))
        ttk.Label(self.root, text="Consulta genérica de registros XML", foreground="#aaaaaa").pack(pady=(0, 12))

        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        form = ttk.LabelFrame(main, text="Dados da consulta")
        form.pack(fill=tk.X, pady=(0, 12))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Buscar estação").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        filter_entry = ttk.Entry(form, textvariable=self.filter_var)
        filter_entry.grid(row=0, column=1, sticky=tk.EW, pady=4)
        filter_entry.bind("<KeyRelease>", lambda _event: self._populate_stations(self.filter_var.get()))

        ttk.Label(form, text="Estação").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.station_list = ttk.Treeview(form, columns=("station",), show="headings", height=4)
        self.station_list.heading("station", text="Nome")
        self.station_list.column("station", anchor=tk.W)
        self.station_list.grid(row=1, column=1, sticky=tk.EW, pady=4)
        self.station_list.bind("<<TreeviewSelect>>", self._select_station)

        ttk.Label(form, text="IP").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.ip_entry = ttk.Entry(form, state="readonly")
        self.ip_entry.grid(row=2, column=1, sticky=tk.EW, pady=4)

        ttk.Label(form, text="KNR").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.knr_entry = ttk.Entry(form)
        self.knr_entry.grid(row=3, column=1, sticky=tk.EW, pady=4)
        self.knr_entry.bind("<Return>", self.consultar)

        actions = ttk.Frame(main)
        actions.pack(fill=tk.X, pady=(0, 12))
        self.query_button = ttk.Button(actions, text="Consultar", command=self.consultar, bootstyle="primary")
        self.query_button.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(actions, text="Limpar", command=self.limpar, bootstyle="secondary").pack(side=tk.LEFT, padx=(0, 8))
        self.open_button = ttk.Button(actions, text="Abrir XML", command=self.abrir_xml, state=tk.DISABLED, bootstyle="info")
        self.open_button.pack(side=tk.LEFT)

        result_frame = ttk.LabelFrame(main, text="Resultado")
        result_frame.pack(fill=tk.X, pady=(0, 12))
        self.result_text = tk.Text(result_frame, height=6, state=tk.DISABLED, bg="#2b3035", fg="#e0e0e0", font=("Consolas", 9))
        self.result_text.pack(fill=tk.X)

        history_frame = ttk.LabelFrame(main, text="Histórico desta sessão")
        history_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("consulta", "retorno", "ip", "knr", "sequencia", "estacao", "operador")
        self.history = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)
        headings = ("Consulta", "Data/hora do registro", "IP", "KNR", "Sequência", "Estação", "Operador")
        for column, heading in zip(columns, headings):
            self.history.heading(column, text=heading)
            self.history.column(column, width=130, anchor=tk.CENTER)
        self.history.pack(fill=tk.BOTH, expand=True)
        ttk.Button(history_frame, text="Limpar histórico", command=self.limpar_historico, bootstyle="warning").pack(anchor=tk.W, pady=(8, 0))

        ttk.Label(self.root, textvariable=self.status_var, padding=8).pack(fill=tk.X)

    def _populate_stations(self, query: str = "") -> None:
        for item in self.station_list.get_children():
            self.station_list.delete(item)
        normalized = query.strip().casefold()
        for name in self.stations:
            if normalized in name.casefold():
                self.station_list.insert("", tk.END, values=(name,))

    def _select_station(self, _event=None) -> None:
        selection = self.station_list.selection()
        if not selection:
            return
        name = str(self.station_list.item(selection[0], "values")[0])
        self.ip_entry.configure(state=tk.NORMAL)
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, self.stations[name])
        self.ip_entry.configure(state="readonly")
        self.status_var.set(f"Status: estação selecionada: {name}")

    def consultar(self, _event=None) -> None:
        ip = self.ip_entry.get().strip()
        knr = self.knr_entry.get().strip()
        if not validar_ip(ip):
            messagebox.showwarning("IP inválido", "Selecione uma estação com IP válido.")
            return
        if not validar_knr(knr):
            messagebox.showwarning("KNR inválido", "Informe exatamente 8 dígitos.")
            return
        self.query_button.configure(state=tk.DISABLED)
        self.open_button.configure(state=tk.DISABLED)
        self.root.configure(cursor="watch")
        self.status_var.set("Status: consultando...")
        threading.Thread(target=self._query_worker, args=(ip, knr), daemon=True).start()

    def _query_worker(self, ip: str, knr: str) -> None:
        try:
            result = consultar_knr(ip, knr)
            self.root.after(0, self._show_result, result, ip, knr)
        except (AuthenticationError, CaminhoNaoEncontradoError, KNRNaoEncontradoError) as exc:
            self.root.after(0, messagebox.showerror, "Falha na consulta", str(exc))
        except Exception:
            self.root.after(0, messagebox.showerror, "Erro", "Ocorreu um erro inesperado durante a consulta.")
        finally:
            self.root.after(0, self._finish_query)

    def _show_result(self, result: dict[str, str], ip: str, knr: str) -> None:
        self.xml_atual = result.get("xml_path")
        lines = (
            f"Data       : {result['data']}", f"Hora       : {result['hora']}",
            f"Estação    : {result['estacao']}", f"Operador   : {result['operador']}",
            f"Sequência  : {result['sequencia']}",
        )
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "\n".join(lines))
        self.result_text.configure(state=tk.DISABLED)
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        returned = f"{result['data']} {result['hora']}"
        self.history.insert("", 0, values=(now, returned, ip, knr, result["sequencia"], result["estacao"], result["operador"]))
        if self.xml_atual:
            self.open_button.configure(state=tk.NORMAL)
        self.status_var.set("Status: consulta concluída")

    def _finish_query(self) -> None:
        self.query_button.configure(state=tk.NORMAL)
        self.root.configure(cursor="")

    def abrir_xml(self) -> None:
        if self.xml_atual and Path(self.xml_atual).is_file():
            os.startfile(self.xml_atual)
        else:
            messagebox.showwarning("Arquivo indisponível", "O XML não está mais disponível.")

    def limpar(self) -> None:
        self.xml_atual = None
        self.filter_var.set("")
        self._populate_stations()
        self.ip_entry.configure(state=tk.NORMAL)
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.configure(state="readonly")
        self.knr_entry.delete(0, tk.END)
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.configure(state=tk.DISABLED)
        self.open_button.configure(state=tk.DISABLED)
        self.status_var.set("Status: interface limpa")

    def limpar_historico(self) -> None:
        for item in self.history.get_children():
            self.history.delete(item)
        self.status_var.set("Status: histórico limpo")


def create_app() -> tuple[ttk.Window, SSEExplorerApp]:
    root = ttk.Window(themename="darkly")
    return root, SSEExplorerApp(root)


def main() -> None:
    root, _application = create_app()
    root.mainloop()


if __name__ == "__main__":
    main()
