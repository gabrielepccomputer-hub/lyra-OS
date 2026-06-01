#!/usr/bin/env python3

"""
LYRA OS v2.2 — Full Linux GUI Music Player

Funziona su: Ubuntu, Debian, Raspberry Pi OS, Arch
Dipendenze: PyQt6, yt-dlp, requests
WiFi:  nmcli (NetworkManager) oppure iwlist
BT:    bluetoothctl oppure hcitool
"""

import sys, os, random, subprocess, re, time, threading
import requests

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QListWidget, QListWidgetItem, QFrame,
    QSlider, QScrollArea, QDialog, QDialogButtonBox, QInputDialog, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QTimer, QUrl, QThread, pyqtSignal, QDateTime, QRect, QObject, QEvent
)
from PyQt6.QtGui import (
    QPixmap, QFont, QPainter, QColor, QLinearGradient,
    QRadialGradient, QPainterPath, QPen, QBrush
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

import yt_dlp, math


# ══════════════════════════════════════════════════════════════
#  COLORI
# ══════════════════════════════════════════════════════════════
C_BG      = "#050508"
C_SURF    = "#0D0D15"
C_ELEV    = "#13131F"
C_BORD    = "#1E1A3A"
C_ACC     = "#8B5CF6"
C_ACC2    = "#EC4899"
C_TEXT    = "#F3F0FF"
C_MUTED   = "#6B7280"
C_OK      = "#10B981"
C_WARN    = "#F59E0B"
C_ERR     = "#EF4444"


# ══════════════════════════════════════════════════════════════
#  INTERNAZIONALIZZAZIONE (i18n)
# ══════════════════════════════════════════════════════════════
TRANSLATIONS = {
    "it": {
        "name": "Italiano 🇮🇹",
        "app_title": "LYRA OS v2.3",
        "tab_play": "Play", "tab_search": "Cerca", "tab_library": "Libreria", "tab_system": "Sistema",
        "no_track": "Nessuna traccia", "local_library": "Libreria Locale",
        "search_placeholder": "Cerca artista, canzone, album…", "search_results_n": "risultati",
        "search_ready": "Pronto per la ricerca", "searching": "Cerco", "search_error": "Nessun risultato.",
        "download_start": "Download avviato…", "download_done": "✅ Download completato!", "download_btn": "⬇ Scarica",
        "random": "🎲 Casuale", "forward": "⏩ +10s",
        "library_title": "🎵 Libreria Locale", "library_refresh": "🔄 Aggiorna", "library_empty": "Libreria vuota. Cerca e scarica musica!",
        "wifi_title": "📶 WiFi", "wifi_scan": "Scansiona", "wifi_scanning": "Scansione WiFi in corso…",
        "wifi_found": "Trovate {} reti", "wifi_open": "Aperta", "wifi_connecting": "Connessione a {}…",
        "wifi_ok": "✅ Connesso con successo!", "wifi_err": "❌ Errore: {}", "wifi_pass": "Password per {}:",
        "wifi_connect_title": "Connetti a {}",
        "wifi_disconnect": "Disconnetti", "wifi_forget": "Dimentica rete",
        "wifi_no_tool": "Nessuno strumento WiFi trovato (nmcli / iwlist)",
        "bt_title": "📡 Bluetooth", "bt_scan": "Scansiona", "bt_scanning": "Scansione BT (7s)…",
        "bt_try_hci": "Provo hcitool lescan…", "bt_connect": "Connetti",
        "bt_pair": "Associa dispositivo", "bt_trust": "Considera attendibile",
        "sim_title": "📱 SIM / Modem", "sim_scan": "Scansiona", "sim_scanning": "Ricerca modem…",
        "sim_no_tool": "Nessun modem trovato. Installa modemmanager.", "sim_found": "{} modem trovati",
        "sim_operator": "Operatore: {}", "sim_signal": "Segnale: {}", "sim_state": "Stato: {}",
        "sim_enable": "Abilita SIM", "sim_disable": "Disabilita SIM",
        "net_title": "🌐 Rete", "net_ifaces": "Interfacce di rete", "net_refresh": "Aggiorna",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "Stato: {}",
        "net_dns": "🔷 DNS / Proxy", "net_dns_label": "DNS Server (es: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "Applica DNS", "net_dns_ok": "✅ DNS aggiornato!", "net_dns_err": "❌ Errore DNS: {}",
        "lang_title": "🌍 Lingua / Language", "lang_apply": "Applica",
        "power_title": "⚡ Sistema Linux", "btn_reboot": "🔄 Riavvia", "btn_poweroff": "⏻ Spegni", "btn_exit": "↩ Esci da LYRA",
        "batt_title": "🔋 Stato Batteria", "batt_charging": "In ricarica", "batt_discharging": "Alimentazione da batteria",
        "batt_detail": "{} Carica: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "en": {
        "name": "English 🇬🇧",
        "app_title": "LYRA OS v2.3",
        "tab_play": "Play", "tab_search": "Search", "tab_library": "Library", "tab_system": "System",
        "no_track": "No track", "local_library": "Local Library",
        "search_placeholder": "Search artist, song, album…", "search_results_n": "results",
        "search_ready": "Ready to search", "searching": "Searching", "search_error": "No results.",
        "download_start": "Download started…", "download_done": "✅ Download complete!", "download_btn": "⬇ Download",
        "random": "🎲 Random", "forward": "⏩ +10s",
        "library_title": "🎵 Local Library", "library_refresh": "🔄 Refresh", "library_empty": "Library empty. Search and download music!",
        "wifi_title": "📶 WiFi", "wifi_scan": "Scan", "wifi_scanning": "Scanning WiFi…",
        "wifi_found": "Found {} networks", "wifi_open": "Open", "wifi_connecting": "Connecting to {}…",
        "wifi_ok": "✅ Connected successfully!", "wifi_err": "❌ Error: {}", "wifi_pass": "Password for {}:",
        "wifi_connect_title": "Connect to {}",
        "wifi_disconnect": "Disconnect", "wifi_forget": "Forget network",
        "wifi_no_tool": "No WiFi tool found (nmcli / iwlist)",
        "bt_title": "📡 Bluetooth", "bt_scan": "Scan", "bt_scanning": "BT Scanning (7s)…",
        "bt_try_hci": "Trying hcitool lescan…", "bt_connect": "Connect",
        "bt_pair": "Pair device", "bt_trust": "Trust device",
        "sim_title": "📱 SIM / Modem", "sim_scan": "Scan", "sim_scanning": "Searching modems…",
        "sim_no_tool": "No modem found. Install modemmanager.", "sim_found": "{} modems found",
        "sim_operator": "Operator: {}", "sim_signal": "Signal: {}", "sim_state": "State: {}",
        "sim_enable": "Enable SIM", "sim_disable": "Disable SIM",
        "net_title": "🌐 Network", "net_ifaces": "Network interfaces", "net_refresh": "Refresh",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "State: {}",
        "net_dns": "🔷 DNS / Proxy", "net_dns_label": "DNS Server (e.g. 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "Apply DNS", "net_dns_ok": "✅ DNS updated!", "net_dns_err": "❌ DNS error: {}",
        "lang_title": "🌍 Language", "lang_apply": "Apply",
        "power_title": "⚡ Linux System", "btn_reboot": "🔄 Reboot", "btn_poweroff": "⏻ Shutdown", "btn_exit": "↩ Exit LYRA",
        "batt_title": "🔋 Battery Status", "batt_charging": "Charging", "batt_discharging": "Battery power",
        "batt_detail": "{} Charge: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "fr": {
        "name": "Français 🇫🇷",
        "app_title": "LYRA OS v2.3",
        "tab_play": "Lecture", "tab_search": "Chercher", "tab_library": "Musique", "tab_system": "Système",
        "no_track": "Aucune piste", "local_library": "Bibliothèque locale",
        "search_placeholder": "Chercher artiste, chanson, album…", "search_results_n": "résultats",
        "search_ready": "Prêt à chercher", "searching": "Recherche", "search_error": "Aucun résultat.",
        "download_start": "Téléchargement démarré…", "download_done": "✅ Téléchargement terminé!", "download_btn": "⬇ Télécharger",
        "random": "🎲 Aléatoire", "forward": "⏩ +10s",
        "library_title": "🎵 Bibliothèque locale", "library_refresh": "🔄 Actualiser", "library_empty": "Bibliothèque vide. Cherche et télécharge de la musique!",
        "wifi_title": "📶 WiFi", "wifi_scan": "Scanner", "wifi_scanning": "Scan WiFi en cours…",
        "wifi_found": "{} réseaux trouvés", "wifi_open": "Ouvert", "wifi_connecting": "Connexion à {}…",
        "wifi_ok": "✅ Connecté avec succès!", "wifi_err": "❌ Erreur: {}", "wifi_pass": "Mot de passe pour {}:",
        "wifi_connect_title": "Connecter à {}",
        "wifi_disconnect": "Déconnecter", "wifi_forget": "Oublier le réseau",
        "wifi_no_tool": "Aucun outil WiFi (nmcli / iwlist)",
        "bt_title": "📡 Bluetooth", "bt_scan": "Scanner", "bt_scanning": "Scan BT (7s)…",
        "bt_try_hci": "Essai hcitool lescan…", "bt_connect": "Connecter",
        "bt_pair": "Jumeler l'appareil", "bt_trust": "Faire confiance",
        "sim_title": "📱 SIM / Modem", "sim_scan": "Scanner", "sim_scanning": "Recherche modem…",
        "sim_no_tool": "Aucun modem trouvé. Installez modemmanager.", "sim_found": "{} modems trouvés",
        "sim_operator": "Opérateur: {}", "sim_signal": "Signal: {}", "sim_state": "État: {}",
        "sim_enable": "Activer SIM", "sim_disable": "Désactiver SIM",
        "net_title": "🌐 Réseau", "net_ifaces": "Interfaces réseau", "net_refresh": "Actualiser",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "État: {}",
        "net_dns": "🔷 DNS / Proxy", "net_dns_label": "Serveur DNS (ex: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "Appliquer DNS", "net_dns_ok": "✅ DNS mis à jour!", "net_dns_err": "❌ Erreur DNS: {}",
        "lang_title": "🌍 Langue / Language", "lang_apply": "Appliquer",
        "power_title": "⚡ Système Linux", "btn_reboot": "🔄 Redémarrer", "btn_poweroff": "⏻ Éteindre", "btn_exit": "↩ Quitter LYRA",
        "batt_title": "🔋 État Batterie", "batt_charging": "En charge", "batt_discharging": "Sur batterie",
        "batt_detail": "{} Charge: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "es": {
        "name": "Español 🇪🇸",
        "app_title": "LYRA OS v2.3",
        "tab_play": "Reproducir", "tab_search": "Buscar", "tab_library": "Biblioteca", "tab_system": "Sistema",
        "no_track": "Sin pista", "local_library": "Biblioteca Local",
        "search_placeholder": "Buscar artista, canción, álbum…", "search_results_n": "resultados",
        "search_ready": "Listo para buscar", "searching": "Buscando", "search_error": "Sin resultados.",
        "download_start": "Descarga iniciada…", "download_done": "✅ ¡Descarga completa!", "download_btn": "⬇ Descargar",
        "random": "🎲 Aleatorio", "forward": "⏩ +10s",
        "library_title": "🎵 Biblioteca Local", "library_refresh": "🔄 Actualizar", "library_empty": "Biblioteca vacía. ¡Busca y descarga música!",
        "wifi_title": "📶 WiFi", "wifi_scan": "Escanear", "wifi_scanning": "Escaneando WiFi…",
        "wifi_found": "{} redes encontradas", "wifi_open": "Abierta", "wifi_connecting": "Conectando a {}…",
        "wifi_ok": "✅ ¡Conectado con éxito!", "wifi_err": "❌ Error: {}", "wifi_pass": "Contraseña para {}:",
        "wifi_connect_title": "Conectar a {}",
        "wifi_disconnect": "Desconectar", "wifi_forget": "Olvidar red",
        "wifi_no_tool": "No se encontró herramienta WiFi (nmcli / iwlist)",
        "bt_title": "📡 Bluetooth", "bt_scan": "Escanear", "bt_scanning": "Escaneo BT (7s)…",
        "bt_try_hci": "Probando hcitool lescan…", "bt_connect": "Conectar",
        "bt_pair": "Vincular dispositivo", "bt_trust": "Confiar dispositivo",
        "sim_title": "📱 SIM / Módem", "sim_scan": "Escanear", "sim_scanning": "Buscando módems…",
        "sim_no_tool": "No se encontró módem. Instala modemmanager.", "sim_found": "{} módems encontrados",
        "sim_operator": "Operador: {}", "sim_signal": "Señal: {}", "sim_state": "Estado: {}",
        "sim_enable": "Activar SIM", "sim_disable": "Desactivar SIM",
        "net_title": "🌐 Red", "net_ifaces": "Interfaces de red", "net_refresh": "Actualizar",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "Estado: {}",
        "net_dns": "🔷 DNS / Proxy", "net_dns_label": "Servidor DNS (ej: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "Aplicar DNS", "net_dns_ok": "✅ ¡DNS actualizado!", "net_dns_err": "❌ Error DNS: {}",
        "lang_title": "🌍 Idioma / Language", "lang_apply": "Aplicar",
        "power_title": "⚡ Sistema Linux", "btn_reboot": "🔄 Reiniciar", "btn_poweroff": "⏻ Apagar", "btn_exit": "↩ Salir de LYRA",
        "batt_title": "🔋 Estado Batería", "batt_charging": "Cargando", "batt_discharging": "Con batería",
        "batt_detail": "{} Carga: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "de": {
        "name": "Deutsch 🇩🇪",
        "app_title": "LYRA OS v2.3",
        "tab_play": "Abspielen", "tab_search": "Suchen", "tab_library": "Bibliothek", "tab_system": "System",
        "no_track": "Kein Titel", "local_library": "Lokale Bibliothek",
        "search_placeholder": "Künstler, Song, Album suchen…", "search_results_n": "Ergebnisse",
        "search_ready": "Bereit zum Suchen", "searching": "Suche", "search_error": "Keine Ergebnisse.",
        "download_start": "Download gestartet…", "download_done": "✅ Download abgeschlossen!", "download_btn": "⬇ Herunterladen",
        "random": "🎲 Zufällig", "forward": "⏩ +10s",
        "library_title": "🎵 Lokale Bibliothek", "library_refresh": "🔄 Aktualisieren", "library_empty": "Bibliothek leer. Suche und lade Musik herunter!",
        "wifi_title": "📶 WiFi", "wifi_scan": "Scannen", "wifi_scanning": "WiFi wird gescannt…",
        "wifi_found": "{} Netzwerke gefunden", "wifi_open": "Offen", "wifi_connecting": "Verbinde mit {}…",
        "wifi_ok": "✅ Erfolgreich verbunden!", "wifi_err": "❌ Fehler: {}", "wifi_pass": "Passwort für {}:",
        "wifi_connect_title": "Verbinden mit {}",
        "wifi_disconnect": "Trennen", "wifi_forget": "Netzwerk vergessen",
        "wifi_no_tool": "Kein WLAN-Tool gefunden (nmcli / iwlist)",
        "bt_title": "📡 Bluetooth", "bt_scan": "Scannen", "bt_scanning": "BT-Scan (7s)…",
        "bt_try_hci": "Versuche hcitool lescan…", "bt_connect": "Verbinden",
        "bt_pair": "Gerät koppeln", "bt_trust": "Gerät vertrauen",
        "sim_title": "📱 SIM / Modem", "sim_scan": "Scannen", "sim_scanning": "Suche Modems…",
        "sim_no_tool": "Kein Modem gefunden. Installiere modemmanager.", "sim_found": "{} Modems gefunden",
        "sim_operator": "Anbieter: {}", "sim_signal": "Signal: {}", "sim_state": "Status: {}",
        "sim_enable": "SIM aktivieren", "sim_disable": "SIM deaktivieren",
        "net_title": "🌐 Netzwerk", "net_ifaces": "Netzwerkschnittstellen", "net_refresh": "Aktualisieren",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "Status: {}",
        "net_dns": "🔷 DNS / Proxy", "net_dns_label": "DNS-Server (z.B. 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "DNS anwenden", "net_dns_ok": "✅ DNS aktualisiert!", "net_dns_err": "❌ DNS-Fehler: {}",
        "lang_title": "🌍 Sprache / Language", "lang_apply": "Anwenden",
        "power_title": "⚡ Linux System", "btn_reboot": "🔄 Neustart", "btn_poweroff": "⏻ Ausschalten", "btn_exit": "↩ LYRA beenden",
        "batt_title": "🔋 Akkustatus", "batt_charging": "Lädt", "batt_discharging": "Akkubetrieb",
        "batt_detail": "{} Ladung: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "pt": {
        "name": "Português 🇧🇷",
        "app_title": "LYRA OS v2.3",
        "tab_play": "Reproduzir", "tab_search": "Buscar", "tab_library": "Biblioteca", "tab_system": "Sistema",
        "no_track": "Sem faixa", "local_library": "Biblioteca Local",
        "search_placeholder": "Buscar artista, música, álbum…", "search_results_n": "resultados",
        "search_ready": "Pronto para buscar", "searching": "Buscando", "search_error": "Sem resultados.",
        "download_start": "Download iniciado…", "download_done": "✅ Download completo!", "download_btn": "⬇ Baixar",
        "random": "🎲 Aleatório", "forward": "⏩ +10s",
        "library_title": "🎵 Biblioteca Local", "library_refresh": "🔄 Atualizar", "library_empty": "Biblioteca vazia. Busque e baixe músicas!",
        "wifi_title": "📶 WiFi", "wifi_scan": "Escanear", "wifi_scanning": "Escaneando WiFi…",
        "wifi_found": "{} redes encontradas", "wifi_open": "Aberta", "wifi_connecting": "Conectando a {}…",
        "wifi_ok": "✅ Conectado com sucesso!", "wifi_err": "❌ Erro: {}", "wifi_pass": "Senha para {}:",
        "wifi_connect_title": "Conectar a {}",
        "wifi_disconnect": "Desconectar", "wifi_forget": "Esquecer rede",
        "wifi_no_tool": "Nenhuma ferramenta WiFi encontrada (nmcli / iwlist)",
        "bt_title": "📡 Bluetooth", "bt_scan": "Escanear", "bt_scanning": "Scan BT (7s)…",
        "bt_try_hci": "Tentando hcitool lescan…", "bt_connect": "Conectar",
        "bt_pair": "Parear dispositivo", "bt_trust": "Confiar dispositivo",
        "sim_title": "📱 SIM / Modem", "sim_scan": "Escanear", "sim_scanning": "Buscando modems…",
        "sim_no_tool": "Nenhum modem encontrado. Instale modemmanager.", "sim_found": "{} modems encontrados",
        "sim_operator": "Operadora: {}", "sim_signal": "Sinal: {}", "sim_state": "Estado: {}",
        "sim_enable": "Ativar SIM", "sim_disable": "Desativar SIM",
        "net_title": "🌐 Rede", "net_ifaces": "Interfaces de rede", "net_refresh": "Atualizar",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "Estado: {}",
        "net_dns": "🔷 DNS / Proxy", "net_dns_label": "Servidor DNS (ex: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "Aplicar DNS", "net_dns_ok": "✅ DNS atualizado!", "net_dns_err": "❌ Erro DNS: {}",
        "lang_title": "🌍 Idioma / Language", "lang_apply": "Aplicar",
        "power_title": "⚡ Sistema Linux", "btn_reboot": "🔄 Reiniciar", "btn_poweroff": "⏻ Desligar", "btn_exit": "↩ Sair do LYRA",
        "batt_title": "🔋 Status Bateria", "batt_charging": "Carregando", "batt_discharging": "Na bateria",
        "batt_detail": "{} Carga: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "ja": {
        "name": "日本語 🇯🇵",
        "app_title": "LYRA OS v2.3",
        "tab_play": "再生", "tab_search": "検索", "tab_library": "ライブラリ", "tab_system": "設定",
        "no_track": "トラックなし", "local_library": "ローカルライブラリ",
        "search_placeholder": "アーティスト、曲、アルバムを検索…", "search_results_n": "件の結果",
        "search_ready": "検索準備完了", "searching": "検索中", "search_error": "結果なし。",
        "download_start": "ダウンロード開始…", "download_done": "✅ ダウンロード完了!", "download_btn": "⬇ ダウンロード",
        "random": "🎲 ランダム", "forward": "⏩ +10s",
        "library_title": "🎵 ローカルライブラリ", "library_refresh": "🔄 更新", "library_empty": "ライブラリ空。音楽を検索してダウンロードしてください！",
        "wifi_title": "📶 WiFi", "wifi_scan": "スキャン", "wifi_scanning": "WiFiスキャン中…",
        "wifi_found": "{}個のネットワークが見つかりました", "wifi_open": "オープン", "wifi_connecting": "{}に接続中…",
        "wifi_ok": "✅ 接続成功!", "wifi_err": "❌ エラー: {}", "wifi_pass": "{}のパスワード:",
        "wifi_connect_title": "{}に接続",
        "wifi_disconnect": "切断", "wifi_forget": "ネットワークを忘れる",
        "wifi_no_tool": "WiFiツールが見つかりません (nmcli / iwlist)",
        "bt_title": "📡 Bluetooth", "bt_scan": "スキャン", "bt_scanning": "BTスキャン (7秒)…",
        "bt_try_hci": "hcitool lescanを試みています…", "bt_connect": "接続",
        "bt_pair": "デバイスをペアリング", "bt_trust": "デバイスを信頼",
        "sim_title": "📱 SIM / モデム", "sim_scan": "スキャン", "sim_scanning": "モデムを検索中…",
        "sim_no_tool": "モデムが見つかりません。modemmanagerをインストールしてください。", "sim_found": "{}個のモデムが見つかりました",
        "sim_operator": "オペレーター: {}", "sim_signal": "シグナル: {}", "sim_state": "状態: {}",
        "sim_enable": "SIMを有効化", "sim_disable": "SIMを無効化",
        "net_title": "🌐 ネットワーク", "net_ifaces": "ネットワークインターフェース", "net_refresh": "更新",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "状態: {}",
        "net_dns": "🔷 DNS / プロキシ", "net_dns_label": "DNSサーバー (例: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "DNSを適用", "net_dns_ok": "✅ DNS更新完了!", "net_dns_err": "❌ DNSエラー: {}",
        "lang_title": "🌍 言語 / Language", "lang_apply": "適用",
        "power_title": "⚡ Linuxシステム", "btn_reboot": "🔄 再起動", "btn_poweroff": "⏻ シャットダウン", "btn_exit": "↩ LYRAを終了",
        "batt_title": "🔋 バッテリー状態", "batt_charging": "充電中", "batt_discharging": "バッテリー駆動",
        "batt_detail": "{} 充電: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "zh": {
        "name": "中文 🇨🇳",
        "app_title": "LYRA OS v2.3",
        "tab_play": "播放", "tab_search": "搜索", "tab_library": "音乐库", "tab_system": "设置",
        "no_track": "无曲目", "local_library": "本地音乐库",
        "search_placeholder": "搜索艺术家、歌曲、专辑…", "search_results_n": "个结果",
        "search_ready": "准备搜索", "searching": "搜索中", "search_error": "无结果。",
        "download_start": "下载已开始…", "download_done": "✅ 下载完成!", "download_btn": "⬇ 下载",
        "random": "🎲 随机", "forward": "⏩ +10s",
        "library_title": "🎵 本地音乐库", "library_refresh": "🔄 刷新", "library_empty": "音乐库为空。搜索并下载音乐！",
        "wifi_title": "📶 WiFi", "wifi_scan": "扫描", "wifi_scanning": "正在扫描WiFi…",
        "wifi_found": "找到 {} 个网络", "wifi_open": "开放", "wifi_connecting": "正在连接 {}…",
        "wifi_ok": "✅ 连接成功!", "wifi_err": "❌ 错误: {}", "wifi_pass": "{} 的密码:",
        "wifi_connect_title": "连接到 {}",
        "wifi_disconnect": "断开连接", "wifi_forget": "忘记网络",
        "wifi_no_tool": "未找到WiFi工具 (nmcli / iwlist)",
        "bt_title": "📡 蓝牙", "bt_scan": "扫描", "bt_scanning": "BT扫描 (7秒)…",
        "bt_try_hci": "正在尝试hcitool lescan…", "bt_connect": "连接",
        "bt_pair": "配对设备", "bt_trust": "信任设备",
        "sim_title": "📱 SIM / 调制解调器", "sim_scan": "扫描", "sim_scanning": "正在搜索调制解调器…",
        "sim_no_tool": "未找到调制解调器。请安装modemmanager。", "sim_found": "找到 {} 个调制解调器",
        "sim_operator": "运营商: {}", "sim_signal": "信号: {}", "sim_state": "状态: {}",
        "sim_enable": "启用SIM", "sim_disable": "禁用SIM",
        "net_title": "🌐 网络", "net_ifaces": "网络接口", "net_refresh": "刷新",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "状态: {}",
        "net_dns": "🔷 DNS / 代理", "net_dns_label": "DNS服务器 (例: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "应用DNS", "net_dns_ok": "✅ DNS已更新!", "net_dns_err": "❌ DNS错误: {}",
        "lang_title": "🌍 语言 / Language", "lang_apply": "应用",
        "power_title": "⚡ Linux系统", "btn_reboot": "🔄 重启", "btn_poweroff": "⏻ 关机", "btn_exit": "↩ 退出LYRA",
        "batt_title": "🔋 电池状态", "batt_charging": "充电中", "batt_discharging": "使用电池",
        "batt_detail": "{} 电量: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "ar": {
        "name": "العربية 🇸🇦",
        "app_title": "LYRA OS v2.3",
        "tab_play": "تشغيل", "tab_search": "بحث", "tab_library": "مكتبة", "tab_system": "إعدادات",
        "no_track": "لا يوجد مسار", "local_library": "المكتبة المحلية",
        "search_placeholder": "ابحث عن فنان، أغنية، ألبوم…", "search_results_n": "نتائج",
        "search_ready": "جاهز للبحث", "searching": "جارٍ البحث", "search_error": "لا توجد نتائج.",
        "download_start": "بدأ التنزيل…", "download_done": "✅ اكتمل التنزيل!", "download_btn": "⬇ تنزيل",
        "random": "🎲 عشوائي", "forward": "⏩ +10s",
        "library_title": "🎵 المكتبة المحلية", "library_refresh": "🔄 تحديث", "library_empty": "المكتبة فارغة. ابحث وحمّل الموسيقى!",
        "wifi_title": "📶 واي فاي", "wifi_scan": "مسح", "wifi_scanning": "جارٍ مسح الواي فاي…",
        "wifi_found": "تم العثور على {} شبكة", "wifi_open": "مفتوح", "wifi_connecting": "جارٍ الاتصال بـ {}…",
        "wifi_ok": "✅ تم الاتصال بنجاح!", "wifi_err": "❌ خطأ: {}", "wifi_pass": "كلمة مرور {}:",
        "wifi_connect_title": "الاتصال بـ {}",
        "wifi_disconnect": "قطع الاتصال", "wifi_forget": "نسيان الشبكة",
        "wifi_no_tool": "لم يُعثر على أداة WiFi (nmcli / iwlist)",
        "bt_title": "📡 بلوتوث", "bt_scan": "مسح", "bt_scanning": "مسح BT (7 ثوانٍ)…",
        "bt_try_hci": "جارٍ تجربة hcitool lescan…", "bt_connect": "اتصال",
        "bt_pair": "إقران الجهاز", "bt_trust": "الوثوق بالجهاز",
        "sim_title": "📱 SIM / مودم", "sim_scan": "مسح", "sim_scanning": "البحث عن مودم…",
        "sim_no_tool": "لم يُعثر على مودم. ثبّت modemmanager.", "sim_found": "تم العثور على {} مودم",
        "sim_operator": "المشغّل: {}", "sim_signal": "الإشارة: {}", "sim_state": "الحالة: {}",
        "sim_enable": "تفعيل SIM", "sim_disable": "تعطيل SIM",
        "net_title": "🌐 الشبكة", "net_ifaces": "واجهات الشبكة", "net_refresh": "تحديث",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "الحالة: {}",
        "net_dns": "🔷 DNS / بروكسي", "net_dns_label": "خادم DNS (مثال: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "تطبيق DNS", "net_dns_ok": "✅ تم تحديث DNS!", "net_dns_err": "❌ خطأ DNS: {}",
        "lang_title": "🌍 اللغة / Language", "lang_apply": "تطبيق",
        "power_title": "⚡ نظام Linux", "btn_reboot": "🔄 إعادة التشغيل", "btn_poweroff": "⏻ إيقاف التشغيل", "btn_exit": "↩ الخروج من LYRA",
        "batt_title": "🔋 حالة البطارية", "batt_charging": "يشحن", "batt_discharging": "طاقة البطارية",
        "batt_detail": "{} الشحن: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "ru": {
        "name": "Русский 🇷🇺",
        "app_title": "LYRA OS v2.3",
        "tab_play": "Плеер", "tab_search": "Поиск", "tab_library": "Библиотека", "tab_system": "Система",
        "no_track": "Нет трека", "local_library": "Локальная библиотека",
        "search_placeholder": "Искать исполнителя, песню, альбом…", "search_results_n": "результатов",
        "search_ready": "Готов к поиску", "searching": "Поиск", "search_error": "Нет результатов.",
        "download_start": "Загрузка начата…", "download_done": "✅ Загрузка завершена!", "download_btn": "⬇ Скачать",
        "random": "🎲 Случайно", "forward": "⏩ +10с",
        "library_title": "🎵 Локальная библиотека", "library_refresh": "🔄 Обновить", "library_empty": "Библиотека пуста. Найдите и скачайте музыку!",
        "wifi_title": "📶 WiFi", "wifi_scan": "Сканировать", "wifi_scanning": "Сканирование WiFi…",
        "wifi_found": "Найдено {} сетей", "wifi_open": "Открытая", "wifi_connecting": "Подключение к {}…",
        "wifi_ok": "✅ Успешно подключено!", "wifi_err": "❌ Ошибка: {}", "wifi_pass": "Пароль для {}:",
        "wifi_connect_title": "Подключиться к {}",
        "wifi_disconnect": "Отключить", "wifi_forget": "Забыть сеть",
        "wifi_no_tool": "WiFi инструмент не найден (nmcli / iwlist)",
        "bt_title": "📡 Bluetooth", "bt_scan": "Сканировать", "bt_scanning": "Сканирование BT (7с)…",
        "bt_try_hci": "Пробую hcitool lescan…", "bt_connect": "Подключить",
        "bt_pair": "Сопрячь устройство", "bt_trust": "Доверять устройству",
        "sim_title": "📱 SIM / Модем", "sim_scan": "Сканировать", "sim_scanning": "Поиск модемов…",
        "sim_no_tool": "Модем не найден. Установите modemmanager.", "sim_found": "Найдено {} модемов",
        "sim_operator": "Оператор: {}", "sim_signal": "Сигнал: {}", "sim_state": "Состояние: {}",
        "sim_enable": "Включить SIM", "sim_disable": "Выключить SIM",
        "net_title": "🌐 Сеть", "net_ifaces": "Сетевые интерфейсы", "net_refresh": "Обновить",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "Состояние: {}",
        "net_dns": "🔷 DNS / Прокси", "net_dns_label": "DNS-сервер (напр: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "Применить DNS", "net_dns_ok": "✅ DNS обновлён!", "net_dns_err": "❌ Ошибка DNS: {}",
        "lang_title": "🌍 Язык / Language", "lang_apply": "Применить",
        "power_title": "⚡ Система Linux", "btn_reboot": "🔄 Перезагрузить", "btn_poweroff": "⏻ Выключить", "btn_exit": "↩ Выйти из LYRA",
        "batt_title": "🔋 Статус батареи", "batt_charging": "Заряжается", "batt_discharging": "От батареи",
        "batt_detail": "{} Заряд: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "hi": {
        "name": "हिन्दी 🇮🇳",
        "app_title": "LYRA OS v2.3",
        "tab_play": "चलाएं", "tab_search": "खोज", "tab_library": "लाइब्रेरी", "tab_system": "सिस्टम",
        "no_track": "कोई ट्रैक नहीं", "local_library": "स्थानीय लाइब्रेरी",
        "search_placeholder": "कलाकार, गाना, एल्बम खोजें…", "search_results_n": "परिणाम",
        "search_ready": "खोज के लिए तैयार", "searching": "खोज रहे हैं", "search_error": "कोई परिणाम नहीं।",
        "download_start": "डाउनलोड शुरू…", "download_done": "✅ डाउनलोड पूर्ण!", "download_btn": "⬇ डाउनलोड",
        "random": "🎲 यादृच्छिक", "forward": "⏩ +10s",
        "library_title": "🎵 स्थानीय लाइब्रेरी", "library_refresh": "🔄 ताज़ा करें", "library_empty": "लाइब्रेरी खाली है। संगीत खोजें और डाउनलोड करें!",
        "wifi_title": "📶 WiFi", "wifi_scan": "स्कैन", "wifi_scanning": "WiFi स्कैन हो रहा है…",
        "wifi_found": "{} नेटवर्क मिले", "wifi_open": "खुला", "wifi_connecting": "{} से कनेक्ट हो रहे हैं…",
        "wifi_ok": "✅ सफलतापूर्वक कनेक्ट!", "wifi_err": "❌ त्रुटि: {}", "wifi_pass": "{} का पासवर्ड:",
        "wifi_connect_title": "{} से कनेक्ट",
        "wifi_disconnect": "डिस्कनेक्ट", "wifi_forget": "नेटवर्क भूलें",
        "wifi_no_tool": "कोई WiFi टूल नहीं मिला (nmcli / iwlist)",
        "bt_title": "📡 Bluetooth", "bt_scan": "स्कैन", "bt_scanning": "BT स्कैन (7s)…",
        "bt_try_hci": "hcitool lescan आज़मा रहे हैं…", "bt_connect": "कनेक्ट",
        "bt_pair": "डिवाइस पेयर करें", "bt_trust": "डिवाइस पर भरोसा",
        "sim_title": "📱 SIM / मॉडेम", "sim_scan": "स्कैन", "sim_scanning": "मॉडेम खोज रहे हैं…",
        "sim_no_tool": "कोई मॉडेम नहीं मिला। modemmanager इंस्टॉल करें।", "sim_found": "{} मॉडेम मिले",
        "sim_operator": "ऑपरेटर: {}", "sim_signal": "सिग्नल: {}", "sim_state": "स्थिति: {}",
        "sim_enable": "SIM सक्रिय करें", "sim_disable": "SIM निष्क्रिय करें",
        "net_title": "🌐 नेटवर्क", "net_ifaces": "नेटवर्क इंटरफेस", "net_refresh": "ताज़ा करें",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "स्थिति: {}",
        "net_dns": "🔷 DNS / प्रॉक्सी", "net_dns_label": "DNS सर्वर (जैसे: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "DNS लागू करें", "net_dns_ok": "✅ DNS अपडेट!", "net_dns_err": "❌ DNS त्रुटि: {}",
        "lang_title": "🌍 भाषा / Language", "lang_apply": "लागू करें",
        "power_title": "⚡ Linux सिस्टम", "btn_reboot": "🔄 रीस्टार्ट", "btn_poweroff": "⏻ बंद करें", "btn_exit": "↩ LYRA से बाहर",
        "batt_title": "🔋 बैटरी स्थिति", "batt_charging": "चार्ज हो रही है", "batt_discharging": "बैटरी पर",
        "batt_detail": "{} चार्ज: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "ko": {
        "name": "한국어 🇰🇷",
        "app_title": "LYRA OS v2.3",
        "tab_play": "재생", "tab_search": "검색", "tab_library": "라이브러리", "tab_system": "설정",
        "no_track": "트랙 없음", "local_library": "로컬 라이브러리",
        "search_placeholder": "아티스트, 노래, 앨범 검색…", "search_results_n": "개 결과",
        "search_ready": "검색 준비 완료", "searching": "검색 중", "search_error": "결과 없음.",
        "download_start": "다운로드 시작…", "download_done": "✅ 다운로드 완료!", "download_btn": "⬇ 다운로드",
        "random": "🎲 랜덤", "forward": "⏩ +10s",
        "library_title": "🎵 로컬 라이브러리", "library_refresh": "🔄 새로고침", "library_empty": "라이브러리 비어있음. 음악을 검색하여 다운로드하세요!",
        "wifi_title": "📶 WiFi", "wifi_scan": "스캔", "wifi_scanning": "WiFi 스캔 중…",
        "wifi_found": "{}개 네트워크 발견", "wifi_open": "개방형", "wifi_connecting": "{}에 연결 중…",
        "wifi_ok": "✅ 연결 성공!", "wifi_err": "❌ 오류: {}", "wifi_pass": "{} 비밀번호:",
        "wifi_connect_title": "{}에 연결",
        "wifi_disconnect": "연결 해제", "wifi_forget": "네트워크 잊기",
        "wifi_no_tool": "WiFi 도구를 찾을 수 없음 (nmcli / iwlist)",
        "bt_title": "📡 블루투스", "bt_scan": "스캔", "bt_scanning": "BT 스캔 (7초)…",
        "bt_try_hci": "hcitool lescan 시도 중…", "bt_connect": "연결",
        "bt_pair": "기기 페어링", "bt_trust": "기기 신뢰",
        "sim_title": "📱 SIM / 모뎀", "sim_scan": "스캔", "sim_scanning": "모뎀 검색 중…",
        "sim_no_tool": "모뎀을 찾을 수 없음. modemmanager를 설치하세요.", "sim_found": "{}개 모뎀 발견",
        "sim_operator": "통신사: {}", "sim_signal": "신호: {}", "sim_state": "상태: {}",
        "sim_enable": "SIM 활성화", "sim_disable": "SIM 비활성화",
        "net_title": "🌐 네트워크", "net_ifaces": "네트워크 인터페이스", "net_refresh": "새로고침",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "상태: {}",
        "net_dns": "🔷 DNS / 프록시", "net_dns_label": "DNS 서버 (예: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "DNS 적용", "net_dns_ok": "✅ DNS 업데이트됨!", "net_dns_err": "❌ DNS 오류: {}",
        "lang_title": "🌍 언어 / Language", "lang_apply": "적용",
        "power_title": "⚡ Linux 시스템", "btn_reboot": "🔄 재시작", "btn_poweroff": "⏻ 종료", "btn_exit": "↩ LYRA 종료",
        "batt_title": "🔋 배터리 상태", "batt_charging": "충전 중", "batt_discharging": "배터리 사용 중",
        "batt_detail": "{} 충전: {}%  •  {}", "time_fmt": "HH:mm",
    },
    "tr": {
        "name": "Türkçe 🇹🇷",
        "app_title": "LYRA OS v2.3",
        "tab_play": "Çal", "tab_search": "Ara", "tab_library": "Kitaplık", "tab_system": "Sistem",
        "no_track": "Parça yok", "local_library": "Yerel Kitaplık",
        "search_placeholder": "Sanatçı, şarkı, albüm ara…", "search_results_n": "sonuç",
        "search_ready": "Aramaya hazır", "searching": "Aranıyor", "search_error": "Sonuç yok.",
        "download_start": "İndirme başladı…", "download_done": "✅ İndirme tamamlandı!", "download_btn": "⬇ İndir",
        "random": "🎲 Rastgele", "forward": "⏩ +10s",
        "library_title": "🎵 Yerel Kitaplık", "library_refresh": "🔄 Yenile", "library_empty": "Kitaplık boş. Müzik ara ve indir!",
        "wifi_title": "📶 WiFi", "wifi_scan": "Tara", "wifi_scanning": "WiFi taranıyor…",
        "wifi_found": "{} ağ bulundu", "wifi_open": "Açık", "wifi_connecting": "{}′e bağlanıyor…",
        "wifi_ok": "✅ Başarıyla bağlandı!", "wifi_err": "❌ Hata: {}", "wifi_pass": "{} şifresi:",
        "wifi_connect_title": "{}′e Bağlan",
        "wifi_disconnect": "Bağlantıyı kes", "wifi_forget": "Ağı unut",
        "wifi_no_tool": "WiFi aracı bulunamadı (nmcli / iwlist)",
        "bt_title": "📡 Bluetooth", "bt_scan": "Tara", "bt_scanning": "BT Tarama (7s)…",
        "bt_try_hci": "hcitool lescan deneniyor…", "bt_connect": "Bağlan",
        "bt_pair": "Cihaz eşleştir", "bt_trust": "Cihaza güven",
        "sim_title": "📱 SIM / Modem", "sim_scan": "Tara", "sim_scanning": "Modem aranıyor…",
        "sim_no_tool": "Modem bulunamadı. modemmanager kur.", "sim_found": "{} modem bulundu",
        "sim_operator": "Operatör: {}", "sim_signal": "Sinyal: {}", "sim_state": "Durum: {}",
        "sim_enable": "SIM etkinleştir", "sim_disable": "SIM devre dışı",
        "net_title": "🌐 Ağ", "net_ifaces": "Ağ arayüzleri", "net_refresh": "Yenile",
        "net_ip": "IP: {}", "net_mac": "MAC: {}", "net_state": "Durum: {}",
        "net_dns": "🔷 DNS / Proxy", "net_dns_label": "DNS Sunucusu (örn: 8.8.8.8, 1.1.1.1):",
        "net_apply_dns": "DNS uygula", "net_dns_ok": "✅ DNS güncellendi!", "net_dns_err": "❌ DNS hatası: {}",
        "lang_title": "🌍 Dil / Language", "lang_apply": "Uygula",
        "power_title": "⚡ Linux Sistemi", "btn_reboot": "🔄 Yeniden başlat", "btn_poweroff": "⏻ Kapat", "btn_exit": "↩ LYRA′dan çık",
        "batt_title": "🔋 Pil Durumu", "batt_charging": "Şarj oluyor", "batt_discharging": "Pil gücü",
        "batt_detail": "{} Şarj: {}%  •  {}", "time_fmt": "HH:mm",
    },
}

# Lingua corrente (default: italiano)
_current_lang = "it"

def tr(key, *args):
    """Ottieni stringa tradotta nella lingua corrente."""
    lang_dict = TRANSLATIONS.get(_current_lang, TRANSLATIONS["it"])
    val = lang_dict.get(key, TRANSLATIONS["it"].get(key, key))
    if args:
        try: return val.format(*args)
        except: return val
    return val

def set_language(lang_code):
    global _current_lang
    if lang_code in TRANSLATIONS:
        _current_lang = lang_code


# ══════════════════════════════════════════════════════════════
#  WIDGET: SPECTRUM VISUALIZER
# ══════════════════════════════════════════════════════════════
class SpectrumVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(55)
        self.bars    = [0.04] * 28
        self.targets = [0.04] * 28
        self.playing = False
        self._t = 0.0
        t = QTimer(self); t.timeout.connect(self._tick); t.start(38)

    def set_playing(self, v): self.playing = v

    def _tick(self):
        self._t += 0.09
        for i in range(28):
            if self.playing:
                ph = i * 0.45 + self._t
                n  = (math.sin(ph*1.8)*0.3 + math.sin(ph*3.2)*0.2
                      + math.sin(ph*0.8+self._t*2)*0.25 + random.uniform(-0.04,0.04))
                self.targets[i] = max(0.04, min(1.0, 0.44+n))
            else:
                self.targets[i] = 0.03 + 0.015*math.sin(i*0.5+self._t*0.25)
        for i in range(28):
            d = self.targets[i]-self.bars[i]
            self.bars[i] += d*(0.38 if d>0 else 0.11)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        bw = w/28
        for i, v in enumerate(self.bars):
            bh = max(3, int(v*h))
            x  = int(i*bw)
            r  = int(139+(236-139)*i/27)
            g  = int(92 +(72 -92 )*i/27)
            b  = int(246+(153-246)*i/27)
            p.setBrush(QBrush(QColor(r,g,b,int(115+140*v))))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(x+1, h-bh, int(bw)-2, bh, 2, 2)
        p.end()


# ══════════════════════════════════════════════════════════════
#  WIDGET: COPERTINA GLOW
# ══════════════════════════════════════════════════════════════
class GlowCover(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(210, 210)
        self._pix = None; self._t = 0.0
        t = QTimer(self); t.timeout.connect(self._tick); t.start(45)

    def set_pixmap(self, pix):
        if pix and not pix.isNull():
            self._pix = pix.scaled(190,190,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation)
        else:
            self._pix = None
        self.update()

    def _tick(self):
        self._t += 0.055; self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        alpha = int(35+30*math.sin(self._t))
        g = QRadialGradient(w/2,h/2,w/2)
        g.setColorAt(0.5, QColor(139,92,246,alpha))
        g.setColorAt(0.75,QColor(236,72,153,alpha//2))
        g.setColorAt(1.0, QColor(0,0,0,0))
        p.setBrush(QBrush(g)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0,0,w,h)
        path = QPainterPath()
        path.addRoundedRect(8,8,194,194,14,14)
        p.fillPath(path, QColor(C_ELEV))
        if self._pix:
            p.setClipPath(path)
            p.drawPixmap(8,8,self._pix)
            p.setClipping(False)
        else:
            p.setPen(QColor(C_MUTED))
            p.setFont(QFont("sans-serif",50))
            p.drawText(QRect(8,8,194,194), Qt.AlignmentFlag.AlignCenter, "♪")
        p.setPen(QPen(QColor(139,92,246,150),2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(8,8,194,194,14,14)
        p.end()


# ══════════════════════════════════════════════════════════════
#  WIDGET: GLASS BUTTON
# ══════════════════════════════════════════════════════════════
class GBtn(QPushButton):
    def __init__(self, txt, accent=False, danger=False, parent=None):
        super().__init__(txt, parent)
        self.setFixedHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if accent:
            s = ("QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                 "stop:0 #7C3AED,stop:1 #DB2777);color:#fff;border:none;"
                 "border-radius:10px;font-weight:800;font-size:13px;padding:0 16px;}"
                 "QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                 "stop:0 #8B5CF6,stop:1 #EC4899);}"
                 "QPushButton:pressed{background:#4C1D95;}"
                 "QPushButton:disabled{background:#2D1B69;color:#6B7280;}")
        elif danger:
            s = ("QPushButton{background:#1A0808;color:#EF4444;border:1.5px solid #EF4444;"
                 "border-radius:10px;font-weight:700;font-size:13px;padding:0 16px;}"
                 "QPushButton:hover{background:#2D0A0A;}"
                 "QPushButton:pressed{background:#450A0A;}")
        else:
            s = ("QPushButton{background:#13131F;color:#C4B5FD;border:1.5px solid #2E1A4A;"
                 "border-radius:10px;font-weight:700;font-size:13px;padding:0 16px;}"
                 "QPushButton:hover{background:#1E1A3A;border-color:#7C3AED;}"
                 "QPushButton:pressed{background:#0D0D15;}"
                 "QPushButton:disabled{color:#3B3060;border-color:#1A1530;}")
        self.setStyleSheet(s)


# ══════════════════════════════════════════════════════════════
#  WIDGET: VIRTUAL KEYBOARD
# ══════════════════════════════════════════════════════════════
class VirtualKeyboard(QWidget):
    key_pressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_SURF};border:1px solid {C_BORD};border-radius:12px;")
        lay = QVBoxLayout(self); lay.setContentsMargins(5,5,5,5); lay.setSpacing(3)
        
        for row in [
            ['1','2','3','4','5','6','7','8','9','0','⌫'],
            ['Q','W','E','R','T','Y','U','I','O','P'],
            ['A','S','D','F','G','H','J','K','L','SPACE'],
            ['Z','X','C','V','B','N','M','-','_','↵'],
        ]:
            rl = QHBoxLayout(); rl.setSpacing(3)
            for k in row:
                b = QPushButton(k)
                # CRITICO: NoFocus altrimenti ruba il focus alla QLineEdit e la tastiera si chiude
                b.setFocusPolicy(Qt.FocusPolicy.NoFocus) 
                
                if k in ('⌫','SPACE','↵'):
                    b.setStyleSheet("QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                        "stop:0 #5B21B6,stop:1 #9D174D);color:#fff;border-radius:7px;"
                        "font-weight:800;font-size:11px;padding:6px 2px;border:none;}"
                        "QPushButton:pressed{background:#3B0764;}")
                    if k=='SPACE': b.setFixedWidth(85)
                else:
                    b.setStyleSheet("QPushButton{background:#1A1530;color:#C4B5FD;"
                        "border-radius:7px;font-weight:700;font-size:12px;"
                        "padding:6px 2px;border:1px solid #2D1F5E;}"
                        "QPushButton:pressed{background:#2E1065;}")
                b.clicked.connect(lambda _, kk=k: self.key_pressed.emit(kk))
                rl.addWidget(b)
            lay.addLayout(rl)


# ══════════════════════════════════════════════════════════════
#  EVENT FILTER: MOSTRA TASTIERA AUTOMATICA
# ══════════════════════════════════════════════════════════════
class InputEventFilter(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def eventFilter(self, obj, event):
        # Se clicchiamo su una QLineEdit, mostriamo la tastiera virtuale
        if isinstance(obj, QLineEdit) and event.type() == QEvent.Type.MouseButtonPress:
            self.main_window.show_keyboard(obj)
        return super().eventFilter(obj, event)


# ══════════════════════════════════════════════════════════════
#  WIDGET: SEARCH RESULT CARD
# ══════════════════════════════════════════════════════════════
class SearchCard(QWidget):
    play_clicked    = pyqtSignal(dict)

    def __init__(self, info: dict, parent=None):
        super().__init__(parent)
        self.info = info
        self.setFixedHeight(72)
        self.setStyleSheet(f"background:{C_ELEV};border:1px solid {C_BORD};border-radius:10px;")
        lay = QHBoxLayout(self); lay.setContentsMargins(8,6,8,6); lay.setSpacing(10)

        self.thumb = QLabel()
        self.thumb.setFixedSize(56,56)
        self.thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb.setStyleSheet(f"background:{C_SURF};border-radius:6px;color:{C_MUTED};font-size:22px;")
        self.thumb.setText("♪")
        lay.addWidget(self.thumb)

        txt = QVBoxLayout(); txt.setSpacing(2)
        self.lbl_title  = QLabel(info.get('title','?')[:52])
        self.lbl_title.setStyleSheet("color:#F3F0FF;font-weight:700;font-size:13px;background:transparent;border:none;")
        self.lbl_artist = QLabel(info.get('artist','')[:40])
        self.lbl_artist.setStyleSheet("color:#A78BFA;font-size:11px;background:transparent;border:none;")
        
        dur = int(info.get('duration') or 0)
        dur_s = f"{dur//60}:{dur%60:02d}" if dur else "—"
        
        self.lbl_meta = QLabel(f"⏱ {dur_s}  •  {info.get('views_str','')}")
        self.lbl_meta.setStyleSheet(f"color:{C_MUTED};font-size:10px;background:transparent;border:none;")
        txt.addWidget(self.lbl_title)
        txt.addWidget(self.lbl_artist)
        txt.addWidget(self.lbl_meta)
        lay.addLayout(txt,1)

        btn_dl = GBtn(tr("download_btn"), accent=True)
        btn_dl.setFixedSize(105,36)
        btn_dl.clicked.connect(lambda: self.play_clicked.emit(self.info))
        lay.addWidget(btn_dl)

        QTimer.singleShot(50, self._load_thumb)

    def _load_thumb(self):
        url = self.info.get('thumbnail','')
        if not url: return
        try:
            data = requests.get(url, timeout=3).content
            pix  = QPixmap(); pix.loadFromData(data)
            if not pix.isNull():
                self.thumb.setPixmap(
                    pix.scaled(56,56,Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation))
                self.thumb.setText("")
        except: pass


# ══════════════════════════════════════════════════════════════
#  THREAD: SEARCH
# ══════════════════════════════════════════════════════════════
class SearchWorker(QThread):
    results = pyqtSignal(list)
    status  = pyqtSignal(str)
    error   = pyqtSignal(str)

    def __init__(self, query, max_results=25):
        super().__init__()
        self.query       = query
        self.max_results = max(1, min(100, max_results))

    def run(self):
        self.status.emit(f"🔍  {tr('searching')} '{self.query}'…")
        opts = {
            'quiet': True, 'extract_flat': True,
            'default_search': 'ytsearch',
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                res = ydl.extract_info(
                    f"ytsearch{self.max_results}:{self.query}",
                    download=False)
            if not res or not res.get('entries'):
                self.error.emit(tr("search_error")); return

            out = []
            for e in res['entries'][:self.max_results]:
                if not e: continue
                dur = e.get('duration') or 0
                views = e.get('view_count') or 0
                vs = f"{views//1000}K views" if views >= 1000 else (f"{views} views" if views else "")
                out.append({
                    'id':        e.get('id',''),
                    'url':       e.get('url') or f"https://www.youtube.com/watch?v={e.get('id','')}",
                    'title':     e.get('title','Senza titolo'),
                    'artist':    e.get('uploader','YouTube'),
                    'thumbnail': e.get('thumbnail',''),
                    'duration':  dur,
                    'views_str': vs,
                })
            self.status.emit(f"✅  {len(out)} {tr('search_results_n')}")
            self.results.emit(out)
        except Exception as ex:
            self.error.emit(str(ex)[:80])


# ══════════════════════════════════════════════════════════════
#  THREAD: DOWNLOAD
# ══════════════════════════════════════════════════════════════
class DownloadWorker(QThread):
    finished = pyqtSignal(dict)
    status   = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, info: dict, music_dir: str):
        super().__init__()
        self.info      = info
        self.music_dir = music_dir

    def run(self):
        self.status.emit(f"⬇  Download: {self.info['title'][:35]}…")
        title_clean = re.sub(r'[^\w\s-]','', self.info['title']).strip()[:80]
        opts = {
            'format':      'm4a/bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl':     os.path.join(self.music_dir, f"{title_clean}.%(ext)s"),
            'quiet':       True, 'no_warnings': True, 'nocheckcertificate': True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                full = ydl.extract_info(self.info['url'], download=True)
                path = ydl.prepare_filename(full)
                self.finished.emit({
                    'title':     full.get('title', title_clean),
                    'artist':    full.get('uploader', self.info.get('artist','YouTube')),
                    'cover':     full.get('thumbnail', self.info.get('thumbnail','')),
                    'file':      path,
                })
        except Exception as ex:
            self.error.emit(str(ex)[:80])


# ══════════════════════════════════════════════════════════════
#  THREAD: WIFI SCAN
# ══════════════════════════════════════════════════════════════
class WifiScanWorker(QThread):
    done  = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        nets = self._try_nmcli()
        if nets is None: nets = self._try_iwlist()
        if nets is None:
            self.error.emit(tr("wifi_no_tool"))
            return
        nets.sort(key=lambda x: -x['signal'])
        self.done.emit(nets)

    def _try_nmcli(self):
        try:
            subprocess.run(['nmcli','dev','wifi','rescan'], capture_output=True, timeout=6)
            time.sleep(1.5)
            out = subprocess.check_output(
                ['nmcli','-t','-f','SSID,SIGNAL,SECURITY,ACTIVE','dev','wifi','list'],
                stderr=subprocess.DEVNULL, text=True, timeout=10)
            nets = []; seen = set()
            for line in out.strip().splitlines():
                parts = line.split(':')
                if len(parts) < 3: continue
                ssid = parts[0].strip()
                if not ssid or ssid in seen: continue
                seen.add(ssid)
                try: sig = int(parts[1])
                except: sig = 0
                sec    = parts[2] if parts[2] else "Aperta"
                active = len(parts)>3 and parts[3].strip().lower() in ('yes','sì','si')
                bars   = "▂▄▆█"[min(3,sig//26)]
                nets.append({'ssid':ssid,'signal':sig,'bars':bars,'security':sec,'active':active})
            return nets if nets else []
        except: return None

    def _try_iwlist(self):
        try:
            ifaces = subprocess.check_output(['iwconfig'], stderr=subprocess.STDOUT, text=True)
            wlan = None
            for line in ifaces.splitlines():
                if 'IEEE 802' in line or 'ESSID' in line: wlan = line.split()[0]; break
            if not wlan: return None
            out = subprocess.check_output(['sudo','iwlist', wlan,'scan'], stderr=subprocess.DEVNULL, text=True, timeout=10)
            nets=[]; seen=set(); cur = {}
            for line in out.splitlines():
                line=line.strip()
                if 'Cell' in line and 'Address' in line:
                    if cur.get('ssid') and cur['ssid'] not in seen: seen.add(cur['ssid']); nets.append(cur)
                    cur={}
                m = re.search(r'ESSID:"(.*?)"',line)
                if m: cur['ssid']=m.group(1)
                m = re.search(r'Signal level=(-?\d+)',line)
                if m:
                    dbm=int(m.group(1)); sig=max(0,min(100,2*(dbm+100)))
                    cur['signal']=sig; cur['bars']="▂▄▆█"[min(3,sig//26)]
                if 'Encryption key:on' in line:  cur['security']='WPA'
                if 'Encryption key:off' in line: cur['security']='Aperta'
                cur.setdefault('active',False)
            if cur.get('ssid') and cur['ssid'] not in seen: nets.append(cur)
            return nets
        except: return None


# ══════════════════════════════════════════════════════════════
#  THREAD: BLUETOOTH SCAN
# ══════════════════════════════════════════════════════════════
class BtScanWorker(QThread):
    found    = pyqtSignal(str, str)
    scanning = pyqtSignal(bool)
    log      = pyqtSignal(str)

    def run(self):
        self.scanning.emit(True)
        ok = self._try_bluetoothctl()
        if not ok: self._try_hcitool()
        self.scanning.emit(False)

    def _try_bluetoothctl(self):
        try:
            subprocess.run(['rfkill','unblock','bluetooth'], capture_output=True)
            subprocess.run(['bluetoothctl','power','on'], capture_output=True, timeout=4)
            time.sleep(0.5)
            proc = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            proc.stdin.write("scan on\n"); proc.stdin.flush()
            self.log.emit(tr("bt_scanning"))
            time.sleep(7)
            proc.stdin.write("devices\n"); proc.stdin.flush()
            time.sleep(0.8)
            out,_ = proc.communicate(input="scan off\nquit\n", timeout=5)
            for line in out.splitlines():
                m = re.search(r'Device\s+([0-9A-Fa-f:]{17})\s+(.*)', line)
                if m: self.found.emit(m.group(1), m.group(2).strip())
            return True
        except: return False

    def _try_hcitool(self):
        try:
            self.log.emit(tr("bt_try_hci"))
            proc = subprocess.Popen(['sudo','hcitool','lescan','--duplicates'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            end = time.time()+7
            while time.time()<end:
                line = proc.stdout.readline()
                if not line: break
                m = re.search(r'([0-9A-Fa-f:]{17})\s+(.*)',line.strip())
                if m and m.group(2)!='(unknown)': self.found.emit(m.group(1), m.group(2).strip())
            proc.terminate()
        except Exception as ex:
            self.log.emit(f"hcitool: {ex}")


# ══════════════════════════════════════════════════════════════
#  THREAD: CONNECT WIFI
# ══════════════════════════════════════════════════════════════
class WifiConnectWorker(QThread):
    done = pyqtSignal(bool, str)
    def __init__(self, ssid, password=""):
        super().__init__()
        self.ssid=ssid; self.password=password

    def run(self):
        try:
            cmd=['nmcli','dev','wifi','connect',self.ssid,'password',self.password] if self.password else ['nmcli','dev','wifi','connect',self.ssid]
            r = subprocess.run(cmd,capture_output=True,text=True,timeout=20)
            ok = r.returncode==0 or 'successfully' in r.stdout.lower()
            msg = r.stdout.strip() or r.stderr.strip()
            self.done.emit(ok, msg[:60])
        except Exception as ex:
            self.done.emit(False, str(ex)[:60])


# ══════════════════════════════════════════════════════════════
#  THREAD: SIM / MODEM SCAN (mmcli)
# ══════════════════════════════════════════════════════════════
class SimScanWorker(QThread):
    done  = pyqtSignal(list)   # lista di dict con info modem
    error = pyqtSignal(str)
    log   = pyqtSignal(str)

    def run(self):
        self.log.emit(tr("sim_scanning"))
        modems = self._try_mmcli()
        if modems is None:
            self.error.emit(tr("sim_no_tool"))
            return
        self.done.emit(modems)

    def _try_mmcli(self):
        try:
            subprocess.run(['which','mmcli'], check=True, capture_output=True)
        except Exception:
            return None
        try:
            out = subprocess.check_output(['mmcli','-L'], text=True, timeout=8, stderr=subprocess.DEVNULL)
            modems = []
            for line in out.splitlines():
                m = re.search(r'/org/freedesktop/ModemManager\d*/Modem/(\d+)', line)
                if m:
                    idx = m.group(1)
                    info = self._modem_info(idx)
                    modems.append(info)
            return modems
        except Exception as ex:
            return []

    def _modem_info(self, idx):
        try:
            out = subprocess.check_output(['mmcli','-m', idx], text=True, timeout=6, stderr=subprocess.DEVNULL)
            info = {'id': idx, 'operator':'?', 'signal':'?', 'state':'?', 'tech':'?', 'imei':'?'}
            for line in out.splitlines():
                line = line.strip()
                if 'operator name' in line.lower():
                    info['operator'] = line.split(':', 1)[-1].strip()
                if 'signal quality' in line.lower():
                    m = re.search(r'(\d+)', line)
                    if m: info['signal'] = m.group(1) + '%'
                if 'state' in line.lower() and 'power' not in line.lower() and 'access' not in line.lower():
                    info['state'] = line.split(':', 1)[-1].strip()
                if 'equipment id' in line.lower() or 'imei' in line.lower():
                    info['imei'] = line.split(':', 1)[-1].strip()
                if 'access tech' in line.lower():
                    info['tech'] = line.split(':', 1)[-1].strip()
            return info
        except:
            return {'id': idx, 'operator':'?', 'signal':'?', 'state':'?', 'tech':'?', 'imei':'?'}


# ══════════════════════════════════════════════════════════════
#  THREAD: NETWORK INTERFACES
# ══════════════════════════════════════════════════════════════
class NetIfaceWorker(QThread):
    done  = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        try:
            ifaces = []
            # Prova con 'ip addr'
            out = subprocess.check_output(['ip','addr'], text=True, timeout=5, stderr=subprocess.DEVNULL)
            cur = None
            for line in out.splitlines():
                m = re.match(r'^\d+:\s+(\S+):', line)
                if m:
                    if cur: ifaces.append(cur)
                    cur = {'name': m.group(1).rstrip('@'), 'ip': '—', 'mac': '—', 'state': '?'}
                    if 'UP' in line:     cur['state'] = 'UP'
                    elif 'DOWN' in line: cur['state'] = 'DOWN'
                    else:                cur['state'] = '?'
                if cur:
                    mi = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                    if mi: cur['ip'] = mi.group(1)
                    mm = re.search(r'link/\S+\s+([0-9a-f:]{17})', line)
                    if mm: cur['mac'] = mm.group(1)
            if cur: ifaces.append(cur)
            self.done.emit(ifaces)
        except Exception as ex:
            self.error.emit(str(ex))


# ══════════════════════════════════════════════════════════════
#  BATTERIA
# ══════════════════════════════════════════════════════════════
def read_battery():
    try:
        base="/sys/class/power_supply"
        for name in os.listdir(base):
            cf=os.path.join(base,name,"capacity")
            sf=os.path.join(base,name,"status")
            if os.path.exists(cf):
                cap=int(open(cf).read().strip())
                stat=open(sf).read().strip() if os.path.exists(sf) else "Unknown"
                return cap, stat in ("Charging","Full")
    except: pass
    return 100, False


# ══════════════════════════════════════════════════════════════
#  LYRA OS — FINESTRA PRINCIPALE
# ══════════════════════════════════════════════════════════════
class LyraOS(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LYRA OS v2.2")
        self.current_file = ""
        self._search_results_cache = []
        self._bt_map = {}
        self._wifi_map = {}   # ssid → security
        self.active_input = None # Tiene traccia dell'input attivo per la tastiera

        self.music_dir = os.path.expanduser("~/music")
        os.makedirs(self.music_dir, exist_ok=True)
        self._purge_broken()

        # Media engine
        self.player = QMediaPlayer()
        self.audio  = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.audio.setVolume(0.85)
        self.player.positionChanged.connect(self._on_pos)
        self.player.durationChanged.connect(self._on_dur)
        self.player.playbackStateChanged.connect(self._on_state)

        self._build_ui()

        # Installa l'Event Filter globale per catturare i click sulle caselle di testo
        self.event_filter = InputEventFilter(self)
        QApplication.instance().installEventFilter(self.event_filter)

        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self._update_statusbar)
        self.sys_timer.start(3000)
        self._update_statusbar()

    def _purge_broken(self):
        for f in os.listdir(self.music_dir):
            if f.endswith((".mp3",".webm")):
                try: os.remove(os.path.join(self.music_dir,f))
                except: pass

    # ─────────────────────── BUILD UI ───────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"""
            QWidget{{background:{C_BG};color:{C_TEXT};font-family:'Segoe UI',sans-serif;}}
            QScrollBar:vertical{{background:{C_SURF};width:5px;border-radius:2px;}}
            QScrollBar::handle:vertical{{background:{C_ACC};border-radius:2px;}}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
            QListWidget{{background:{C_SURF};border:1px solid {C_BORD};border-radius:10px;color:{C_TEXT};outline:0;}}
            QListWidget::item{{padding:8px 12px;border-bottom:1px solid {C_BORD};}}
            QListWidget::item:selected{{background:#2D1B69;}}
            QListWidget::item:hover{{background:#1A1530;}}
            QLineEdit{{background:{C_ELEV};border:1.5px solid {C_BORD};border-radius:9px;color:{C_TEXT};padding:0 12px;font-size:14px;}}
            QLineEdit:focus{{border-color:{C_ACC};}}
        """)
        self.showFullScreen()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        root.addWidget(self._make_statusbar())

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self._make_player_tab()
        self._make_search_tab()
        self._make_library_tab()
        self._make_system_tab()

        # TASTIERA VIRTUALE (Nascosta di default)
        self.vk = VirtualKeyboard()
        self.vk.key_pressed.connect(self._on_vk_key)
        self.vk.hide()
        root.addWidget(self.vk)

        root.addWidget(self._make_tabbar())

    def _make_statusbar(self):
        bar = QFrame()
        bar.setFixedHeight(36)
        bar.setStyleSheet(f"background:{C_SURF};border-bottom:1px solid {C_BORD};")
        lay = QHBoxLayout(bar); lay.setContentsMargins(14,0,14,0)
        self.lbl_logo = QLabel("✦ LYRA OS")
        self.lbl_logo.setStyleSheet("color:#A78BFA;font-size:13px;font-weight:900;letter-spacing:3px;")
        self.lbl_time   = QLabel("--:--")
        self.lbl_time.setStyleSheet("color:#D8B4FE;font-size:13px;font-weight:700;")
        self.lbl_batt   = QLabel("🔋 —")
        self.lbl_batt.setStyleSheet(f"color:{C_MUTED};font-size:12px;")
        self.lbl_wifi_i = QLabel("📵")
        self.lbl_wifi_i.setStyleSheet(f"color:{C_MUTED};font-size:12px;")
        lay.addWidget(self.lbl_logo); lay.addStretch()
        lay.addWidget(self.lbl_wifi_i); lay.addSpacing(10)
        lay.addWidget(self.lbl_batt);  lay.addSpacing(14)
        lay.addWidget(self.lbl_time)
        return bar

    def _make_tabbar(self):
        bar = QFrame()
        bar.setFixedHeight(60)
        bar.setStyleSheet(f"background:{C_SURF};border-top:1px solid {C_BORD};")
        lay = QHBoxLayout(bar); lay.setContentsMargins(8,6,8,6); lay.setSpacing(4)
        self._tab_btns = []
        for i,(icon,lbl) in enumerate([(("▶",tr("tab_play")),("⌕",tr("tab_search")),("♪",tr("tab_library")),("⚙",tr("tab_system")))[i] for i in range(4)]):
            b = QPushButton(f"{icon}  {lbl}")
            b.setCheckable(True)
            b.setFixedHeight(48)
            b.setFont(QFont("Segoe UI Emoji",11,QFont.Weight.Bold))
            b.setStyleSheet(self._tab_style(False))
            b.clicked.connect(lambda _,idx=i: self._switch_tab(idx))
            lay.addWidget(b)
            self._tab_btns.append(b)
        self._tab_btns[0].setChecked(True)
        self._tab_btns[0].setStyleSheet(self._tab_style(True))
        return bar

    def _tab_style(self, active):
        if active:
            return ("QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4C1D95,stop:1 #831843);border:1.5px solid #7C3AED;border-radius:11px;color:#fff;font-weight:800;font-size:12px;padding:0 8px;}")
        return ("QPushButton{background:#0D0D15;border:1.5px solid #1E1A3A;border-radius:11px;color:#6B7280;font-size:12px;padding:0 8px;}QPushButton:hover{background:#13131F;border-color:#3B2A6A;color:#A78BFA;}")

    def _switch_tab(self, idx):
        self.stack.setCurrentIndex(idx)
        for i,b in enumerate(self._tab_btns):
            b.setChecked(i==idx)
            b.setStyleSheet(self._tab_style(i==idx))
        if idx==2: self._refresh_library()
        self.hide_keyboard() # Chiudi la tastiera se cambiamo tab

    # ─────────────────── VIRTUAL KEYBOARD LOGIC ─────────────────
    def show_keyboard(self, target_input):
        self.active_input = target_input
        self.vk.show()

    def hide_keyboard(self):
        self.vk.hide()
        self.active_input = None

    def _on_vk_key(self, key):
        if not self.active_input: return
        if key == '⌫':
            self.active_input.backspace()
        elif key == 'SPACE':
            self.active_input.insert(' ')
        elif key == '↵':
            # Simula la pressione dell'invio sulla casella di testo
            self.active_input.returnPressed.emit()
            self.hide_keyboard()
        else:
            self.active_input.insert(key)

    # ─────────────────── TAB 0: PLAYER ──────────────────────────
    def _make_player_tab(self):
        page = QWidget(); lay = QVBoxLayout(page)
        lay.setContentsMargins(18,10,18,10); lay.setSpacing(8)

        top = QHBoxLayout(); top.setSpacing(18)
        self.glow_cover = GlowCover()
        top.addWidget(self.glow_cover)

        info = QVBoxLayout(); info.setSpacing(4)
        info.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.lbl_title  = QLabel(tr("no_track"))
        self.lbl_title.setFont(QFont("Segoe UI",16,QFont.Weight.Black))
        self.lbl_title.setWordWrap(True)
        self.lbl_artist = QLabel("—")
        self.lbl_artist.setStyleSheet("color:#A78BFA;font-size:13px;font-weight:600;")
        self.lbl_tpos   = QLabel("0:00 / 0:00")
        self.lbl_tpos.setStyleSheet(f"color:{C_MUTED};font-size:11px;")
        info.addWidget(self.lbl_title); info.addWidget(self.lbl_artist)
        info.addStretch(); info.addWidget(self.lbl_tpos)
        top.addLayout(info,1); lay.addLayout(top)

        self.spectrum = SpectrumVisualizer(); lay.addWidget(self.spectrum)

        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.setStyleSheet("""
            QSlider::groove:horizontal{background:#1E1A3A;height:6px;border-radius:3px;}
            QSlider::sub-page:horizontal{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7C3AED,stop:1 #DB2777);border-radius:3px;}
            QSlider::handle:horizontal{background:#fff;width:14px;height:14px;margin:-4px 0;border-radius:7px;border:2px solid #8B5CF6;}""")
        self.seek.sliderMoved.connect(self.player.setPosition)
        lay.addWidget(self.seek)

        vol_r = QHBoxLayout()
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0,100); self.vol_slider.setValue(85)
        self.vol_slider.setFixedWidth(110)
        self.vol_slider.setStyleSheet("""
            QSlider::groove:horizontal{background:#1E1A3A;height:4px;border-radius:2px;}
            QSlider::sub-page:horizontal{background:#7C3AED;border-radius:2px;}
            QSlider::handle:horizontal{background:#A78BFA;width:12px;height:12px;margin:-4px 0;border-radius:6px;}""")
        self.vol_slider.valueChanged.connect(lambda v: self.audio.setVolume(v/100))
        vol_r.addStretch()
        vol_r.addWidget(QLabel("🔉")); vol_r.addWidget(self.vol_slider)
        vol_r.addWidget(QLabel("🔊")); lay.addLayout(vol_r)

        ctrl = QHBoxLayout(); ctrl.setAlignment(Qt.AlignmentFlag.AlignCenter); ctrl.setSpacing(14)
        self.btn_rand = GBtn(tr("random")); self.btn_rand.setFixedSize(108,42)
        self.btn_rand.clicked.connect(self._play_random)

        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedSize(62,62)
        self.btn_play.setStyleSheet("""
            QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #7C3AED,stop:1 #DB2777);color:#fff;font-size:24px;border-radius:31px;border:none;font-weight:900;}
            QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #8B5CF6,stop:1 #EC4899);}
            QPushButton:pressed{background:#4C1D95;}""")
        self.btn_play.clicked.connect(self._toggle_play)

        self.btn_fwd = GBtn(tr("forward")); self.btn_fwd.setFixedSize(108,42)
        self.btn_fwd.clicked.connect(self._forward)

        ctrl.addWidget(self.btn_rand); ctrl.addWidget(self.btn_play); ctrl.addWidget(self.btn_fwd)
        lay.addLayout(ctrl)
        self.stack.addWidget(page)

    # ─────────────────── TAB 1: RICERCA ─────────────────────────
    def _make_search_tab(self):
        page = QWidget(); lay = QVBoxLayout(page)
        lay.setContentsMargins(14,10,14,8); lay.setSpacing(6)

        top = QHBoxLayout(); top.setSpacing(6)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("search_placeholder"))
        self.search_input.setFixedHeight(44)
        self.search_input.returnPressed.connect(self._start_search)

        self.search_count = QLineEdit("25")
        self.search_count.setFixedSize(50,44)
        self.search_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.search_count.setToolTip("Numero di risultati (1–100)")

        btn_go = QPushButton("↵")
        btn_go.setFixedSize(44,44)
        btn_go.setFocusPolicy(Qt.FocusPolicy.NoFocus) # Non ruba focus
        btn_go.setStyleSheet("""
            QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #7C3AED,stop:1 #DB2777);color:#fff;font-size:20px;font-weight:900;border-radius:9px;border:none;}
            QPushButton:pressed{background:#4C1D95;}""")
        btn_go.clicked.connect(self._start_search)
        
        top.addWidget(self.search_input,1)
        top.addWidget(self.search_count)
        top.addWidget(btn_go)
        lay.addLayout(top)

        self.search_status = QLabel(tr("search_ready"))
        self.search_status.setStyleSheet(f"color:{C_MUTED};font-size:11px;padding:2px 6px;")
        lay.addWidget(self.search_status)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        self.search_list_widget = QWidget()
        self.search_list_layout = QVBoxLayout(self.search_list_widget)
        self.search_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.search_list_layout.setSpacing(6)
        scroll.setWidget(self.search_list_widget)
        lay.addWidget(scroll, 1)

        self.stack.addWidget(page)

    # ─────────────────── TAB 2: LIBRERIA ────────────────────────
    def _make_library_tab(self):
        page = QWidget(); lay = QVBoxLayout(page)
        lay.setContentsMargins(14,10,14,8); lay.setSpacing(6)

        h = QHBoxLayout()
        lbl = QLabel(tr("library_title"))
        lbl.setStyleSheet("color:#D8B4FE;font-size:15px;font-weight:800;")
        btn_ref = GBtn(tr("library_refresh"), accent=True)
        btn_ref.clicked.connect(self._refresh_library)
        h.addWidget(lbl); h.addStretch(); h.addWidget(btn_ref)
        lay.addLayout(h)

        self.lib_list = QListWidget()
        self.lib_list.itemDoubleClicked.connect(self._play_local)
        lay.addWidget(self.lib_list, 1)
        self.stack.addWidget(page)

    # ─────────────────── TAB 3: SISTEMA — SCROLLABILE ────────────
    def _make_system_tab(self):
        outer = QWidget()
        outer_lay = QVBoxLayout(outer)
        outer_lay.setContentsMargins(0,0,0,0); outer_lay.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(14,10,14,14); lay.setSpacing(10)

        def section_label(txt):
            lbl = QLabel(txt)
            lbl.setStyleSheet("color:#D8B4FE;font-size:14px;font-weight:800;padding-top:6px;")
            return lbl

        # ── WiFi ──────────────────────────────────────────────────
        lay.addWidget(section_label(tr("wifi_title")))
        w_l = QHBoxLayout()
        self.btn_scan_wifi = GBtn(tr("wifi_scan"), accent=True)
        self.btn_scan_wifi.clicked.connect(self._scan_wifi)
        self.btn_wifi_disconnect = GBtn(tr("wifi_disconnect"))
        self.btn_wifi_disconnect.clicked.connect(self._disconnect_wifi)
        self.btn_wifi_forget = GBtn(tr("wifi_forget"), danger=True)
        self.btn_wifi_forget.clicked.connect(self._forget_wifi)
        w_l.addWidget(self.btn_scan_wifi)
        w_l.addWidget(self.btn_wifi_disconnect)
        w_l.addWidget(self.btn_wifi_forget)
        lay.addLayout(w_l)

        self.wifi_list = QListWidget()
        self.wifi_list.setFixedHeight(130)
        self.wifi_list.itemDoubleClicked.connect(self._connect_wifi_prompt)
        lay.addWidget(self.wifi_list)
        self.wifi_log = QLabel("")
        self.wifi_log.setStyleSheet(f"color:{C_MUTED};font-size:10px;")
        lay.addWidget(self.wifi_log)

        # ── Bluetooth ─────────────────────────────────────────────
        lay.addWidget(section_label(tr("bt_title")))
        b_l = QHBoxLayout()
        self.btn_scan_bt = GBtn(tr("bt_scan"), accent=True)
        self.btn_scan_bt.clicked.connect(self._scan_bt)
        self.btn_bt_connect = GBtn(tr("bt_connect"))
        self.btn_bt_connect.clicked.connect(self._bt_connect_selected)
        self.btn_bt_pair = GBtn(tr("bt_pair"), accent=True)
        self.btn_bt_pair.clicked.connect(self._bt_pair_selected)
        b_l.addWidget(self.btn_scan_bt)
        b_l.addWidget(self.btn_bt_connect)
        b_l.addWidget(self.btn_bt_pair)
        lay.addLayout(b_l)

        self.bt_list = QListWidget()
        self.bt_list.setFixedHeight(120)
        lay.addWidget(self.bt_list)
        self.bt_log = QLabel("")
        self.bt_log.setStyleSheet(f"color:{C_MUTED};font-size:10px;")
        lay.addWidget(self.bt_log)

        # ── SIM / Modem ───────────────────────────────────────────
        lay.addWidget(section_label(tr("sim_title")))
        sim_l = QHBoxLayout()
        self.btn_scan_sim = GBtn(tr("sim_scan"), accent=True)
        self.btn_scan_sim.clicked.connect(self._scan_sim)
        self.btn_sim_enable = GBtn(tr("sim_enable"))
        self.btn_sim_enable.clicked.connect(self._sim_enable)
        self.btn_sim_disable = GBtn(tr("sim_disable"), danger=True)
        self.btn_sim_disable.clicked.connect(self._sim_disable)
        sim_l.addWidget(self.btn_scan_sim)
        sim_l.addWidget(self.btn_sim_enable)
        sim_l.addWidget(self.btn_sim_disable)
        lay.addLayout(sim_l)

        self.sim_list = QListWidget()
        self.sim_list.setFixedHeight(100)
        lay.addWidget(self.sim_list)
        self.sim_log = QLabel("")
        self.sim_log.setStyleSheet(f"color:{C_MUTED};font-size:10px;")
        lay.addWidget(self.sim_log)

        # ── Rete / Network interfaces ─────────────────────────────
        lay.addWidget(section_label(tr("net_title")))
        net_h = QHBoxLayout()
        net_lbl2 = QLabel(tr("net_ifaces"))
        net_lbl2.setStyleSheet(f"color:{C_MUTED};font-size:11px;")
        self.btn_net_refresh = GBtn(tr("net_refresh"), accent=True)
        self.btn_net_refresh.clicked.connect(self._refresh_net)
        net_h.addWidget(net_lbl2); net_h.addStretch(); net_h.addWidget(self.btn_net_refresh)
        lay.addLayout(net_h)

        self.net_list = QListWidget()
        self.net_list.setFixedHeight(100)
        lay.addWidget(self.net_list)

        # DNS
        dns_lbl = QLabel(tr("net_dns"))
        dns_lbl.setStyleSheet("color:#93C5FD;font-size:12px;font-weight:700;")
        lay.addWidget(dns_lbl)
        dns_input_lbl = QLabel(tr("net_dns_label"))
        dns_input_lbl.setStyleSheet(f"color:{C_MUTED};font-size:10px;")
        lay.addWidget(dns_input_lbl)
        dns_row = QHBoxLayout()
        self.dns_input = QLineEdit("8.8.8.8, 1.1.1.1")
        self.dns_input.setFixedHeight(38)
        btn_dns = GBtn(tr("net_apply_dns"), accent=True)
        btn_dns.clicked.connect(self._apply_dns)
        dns_row.addWidget(self.dns_input, 1); dns_row.addWidget(btn_dns)
        lay.addLayout(dns_row)
        self.net_log = QLabel("")
        self.net_log.setStyleSheet(f"color:{C_MUTED};font-size:10px;")
        lay.addWidget(self.net_log)

        # ── Lingua ────────────────────────────────────────────────
        lay.addWidget(section_label(tr("lang_title")))
        lang_scroll_w = QWidget()
        lang_scroll_lay = QHBoxLayout(lang_scroll_w)
        lang_scroll_lay.setSpacing(6); lang_scroll_lay.setContentsMargins(0,0,0,0)
        self._lang_btns = {}
        for code, ldata in TRANSLATIONS.items():
            b = QPushButton(ldata["name"])
            b.setFixedHeight(36)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            is_active = (code == _current_lang)
            b.setStyleSheet(self._lang_btn_style(is_active))
            b.clicked.connect(lambda _, c=code: self._change_language(c))
            lang_scroll_lay.addWidget(b)
            self._lang_btns[code] = b
        lang_scroll_lay.addStretch()
        lang_sa = QScrollArea()
        lang_sa.setWidgetResizable(True)
        lang_sa.setFixedHeight(52)
        lang_sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        lang_sa.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lang_sa.setStyleSheet("QScrollArea{border:1px solid "+C_BORD+";border-radius:8px;background:"+C_SURF+";}")
        lang_sa.setWidget(lang_scroll_w)
        lay.addWidget(lang_sa)

        # ── Power / Sistema ───────────────────────────────────────
        lay.addWidget(section_label(tr("power_title")))
        pwr_lay = QHBoxLayout()
        self.btn_reboot   = GBtn(tr("btn_reboot"), danger=True)
        self.btn_reboot.clicked.connect(lambda: os.system("systemctl reboot"))
        self.btn_poweroff = GBtn(tr("btn_poweroff"), danger=True)
        self.btn_poweroff.clicked.connect(lambda: os.system("systemctl poweroff"))
        self.btn_exit_app = GBtn(tr("btn_exit"))
        self.btn_exit_app.clicked.connect(QApplication.instance().quit)
        pwr_lay.addWidget(self.btn_reboot)
        pwr_lay.addWidget(self.btn_poweroff)
        pwr_lay.addWidget(self.btn_exit_app)
        lay.addLayout(pwr_lay)

        self.lbl_batt_section = section_label(tr("batt_title"))
        lay.addWidget(self.lbl_batt_section)
        self.lbl_batt_detail = QLabel("")
        self.lbl_batt_detail.setStyleSheet(f"color:{C_TEXT};font-size:12px;")
        lay.addWidget(self.lbl_batt_detail)

        lay.addStretch()
        scroll.setWidget(page)
        outer_lay.addWidget(scroll)
        self.stack.addWidget(outer)

    def _lang_btn_style(self, active):
        if active:
            return ("QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                    "stop:0 #7C3AED,stop:1 #DB2777);color:#fff;border:none;"
                    "border-radius:8px;font-weight:800;font-size:11px;padding:0 10px;}")
        return ("QPushButton{background:#13131F;color:#C4B5FD;border:1px solid #2E1A4A;"
                "border-radius:8px;font-weight:600;font-size:11px;padding:0 10px;}"
                "QPushButton:hover{background:#1E1A3A;border-color:#7C3AED;}")


    # ─────────────────── LOGICA PLAYER ──────────────────────────
    def _on_pos(self, msec):
        s = msec // 1000
        self.seek.blockSignals(True)
        self.seek.setValue(msec)
        self.seek.blockSignals(False)
        cur = f"{s//60}:{s%60:02d}"
        tot = self.player.duration() // 1000
        tot_s = f"{tot//60}:{tot%60:02d}"
        self.lbl_tpos.setText(f"{cur} / {tot_s}")

    def _on_dur(self, msec):
        self.seek.setRange(0, msec)

    def _on_state(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_play.setText("⏸")
            self.spectrum.set_playing(True)
        else:
            self.btn_play.setText("▶")
            self.spectrum.set_playing(False)

    def _toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            if self.current_file: self.player.play()
            else: self._play_random()

    def _forward(self):
        self.player.setPosition(self.player.position() + 10000)

    def _play_random(self):
        files = [os.path.join(self.music_dir, f) for f in os.listdir(self.music_dir) 
                 if f.endswith(('.m4a', '.mp3', '.wav', '.flac', '.ogg'))]
        if files:
            self._play_file(random.choice(files))
        else:
            self.search_status.setText(tr("library_empty"))

    def _play_file(self, filepath):
        self.current_file = filepath
        url = QUrl.fromLocalFile(filepath)
        self.player.setSource(url)
        self.player.play()
        fname = os.path.basename(filepath)
        self.lbl_title.setText(fname.rsplit('.', 1)[0])
        self.lbl_artist.setText(tr("local_library"))
        self.glow_cover.set_pixmap(None)


    # ─────────────────── LOGICA RICERCA ─────────────────────────
    def _start_search(self):
        q = self.search_input.text().strip()
        if not q: return
        try: cnt = int(self.search_count.text())
        except ValueError: cnt = 25

        for i in reversed(range(self.search_list_layout.count())): 
            self.search_list_layout.itemAt(i).widget().setParent(None)
        
        self.search_status.setText(f"🔍 {tr('searching')} '{q}'…")
        self.sw = SearchWorker(q, cnt)
        self.sw.results.connect(self._on_search_results)
        self.sw.status.connect(lambda s: self.search_status.setText(s))
        self.sw.error.connect(lambda e: self.search_status.setText(f"❌ {e}"))
        self.sw.start()

    def _on_search_results(self, results):
        self._search_results_cache = results
        for r in results:
            card = SearchCard(r)
            card.play_clicked.connect(self._download_track)
            self.search_list_layout.addWidget(card)

    def _download_track(self, info):
        self.search_status.setText(tr("download_start"))
        self.dw = DownloadWorker(info, self.music_dir)
        self.dw.status.connect(lambda s: self.search_status.setText(s))
        self.dw.finished.connect(self._on_download_done)
        self.dw.error.connect(lambda e: self.search_status.setText(f"❌ {e}"))
        self.dw.start()

    def _on_download_done(self, data):
        self.search_status.setText(tr("download_done"))
        url = data.get('cover', '')
        if url:
            try:
                img_data = requests.get(url, timeout=3).content
                pix = QPixmap(); pix.loadFromData(img_data)
                self.glow_cover.set_pixmap(pix)
            except: pass
        self._play_file(data['file'])


    # ─────────────────── LOGICA LIBRERIA ────────────────────────
    def _refresh_library(self):
        self.lib_list.clear()
        try:
            for f in sorted(os.listdir(self.music_dir)):
                if f.endswith(('.m4a', '.mp3', '.wav', '.flac', '.ogg', '.webm')):
                    item = QListWidgetItem(f"♪  {f}")
                    item.setData(Qt.ItemDataRole.UserRole, os.path.join(self.music_dir, f))
                    self.lib_list.addItem(item)
        except Exception as e:
            pass

    def _play_local(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and os.path.exists(path):
            self._play_file(path)


    # ─────────────────── LOGICA SISTEMA ─────────────────────────
    def _update_statusbar(self):
        now = QDateTime.currentDateTime()
        self.lbl_time.setText(now.toString(tr("time_fmt")))
        cap, charging = read_battery()
        icon = "🔌" if charging else "🔋"
        self.lbl_batt.setText(f"{icon} {cap}%")
        state_str = tr("batt_charging") if charging else tr("batt_discharging")
        self.lbl_batt_detail.setText(tr("batt_detail", icon, cap, state_str))

    # WIFI
    def _scan_wifi(self):
        self.wifi_list.clear()
        self._wifi_map.clear()
        self.wifi_log.setText(tr("wifi_scanning"))
        self.btn_scan_wifi.setEnabled(False)
        self.wsw = WifiScanWorker()
        self.wsw.done.connect(self._on_wifi_done)
        self.wsw.error.connect(lambda e: self.wifi_log.setText(f"❌ {e}"))
        self.wsw.start()

    def _on_wifi_done(self, nets):
        self.btn_scan_wifi.setEnabled(True)
        self.wifi_log.setText(tr("wifi_found", len(nets)))
        self.lbl_wifi_i.setText("📶")
        for n in nets:
            open_str = tr("wifi_open")
            sec_str = f" 🔒 {n['security']}" if n['security'] != 'Aperta' and n['security'] != open_str else f" 📶 {open_str}"
            active_str = " ✔" if n.get('active') else ""
            txt = f"{n['bars']}  {n['ssid']}{sec_str} ({n['signal']}%){active_str}"
            item = QListWidgetItem(txt)
            item.setData(Qt.ItemDataRole.UserRole, n['ssid'])
            self.wifi_list.addItem(item)
            self._wifi_map[n['ssid']] = n['security']

    def _connect_wifi_prompt(self, item):
        ssid = item.data(Qt.ItemDataRole.UserRole)
        sec = self._wifi_map.get(ssid, 'WPA')
        pwd = ""
        open_str = tr("wifi_open")
        if sec != 'Aperta' and sec != open_str:
            dialog = QDialog(self)
            dialog.setWindowTitle(tr("wifi_connect_title", ssid))
            dialog.setStyleSheet(f"background:{C_ELEV}; color:{C_TEXT};")
            lay = QVBoxLayout(dialog)
            lay.addWidget(QLabel(tr("wifi_pass", ssid)))
            pwd_input = QLineEdit()
            pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
            lay.addWidget(pwd_input)
            btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            btn_box.setStyleSheet("background:transparent; color:white;")
            btn_box.accepted.connect(dialog.accept)
            btn_box.rejected.connect(dialog.reject)
            lay.addWidget(btn_box)
            pwd_input.setFocus()
            if dialog.exec() == QDialog.DialogCode.Accepted:
                pwd = pwd_input.text()
            else:
                return
        self.wifi_log.setText(tr("wifi_connecting", ssid))
        self.wcw = WifiConnectWorker(ssid, pwd)
        self.wcw.done.connect(self._on_wifi_connected)
        self.wcw.start()

    def _on_wifi_connected(self, ok, msg):
        if ok:
            self.wifi_log.setText(tr("wifi_ok"))
        else:
            self.wifi_log.setText(tr("wifi_err", msg))

    # BLUETOOTH
    def _scan_bt(self):
        self.bt_list.clear()
        self._bt_map.clear()
        self.bt_log.setText(tr("bt_scanning"))
        self.btn_scan_bt.setEnabled(False)
        self.bsw = BtScanWorker()
        self.bsw.found.connect(self._on_bt_found)
        self.bsw.scanning.connect(lambda s: self.btn_scan_bt.setEnabled(not s))
        self.bsw.log.connect(lambda s: self.bt_log.setText(s))
        self.bsw.start()

    def _on_bt_found(self, mac, name):
        if mac not in self._bt_map:
            self._bt_map[mac] = name
            item = QListWidgetItem(f"🎧 {name} ({mac})")
            item.setData(Qt.ItemDataRole.UserRole, mac)
            self.bt_list.addItem(item)

    def _bt_connect_selected(self):
        item = self.bt_list.currentItem()
        if not item: return
        mac = item.data(Qt.ItemDataRole.UserRole)
        self.bt_log.setText(f"Connecting {mac}…")
        def _do():
            try:
                subprocess.run(['bluetoothctl','connect', mac], capture_output=True, timeout=10)
                self.bt_log.setText(f"✅ {mac}")
            except Exception as e:
                self.bt_log.setText(f"❌ {e}")
        threading.Thread(target=_do, daemon=True).start()

    def _bt_pair_selected(self):
        item = self.bt_list.currentItem()
        if not item: return
        mac = item.data(Qt.ItemDataRole.UserRole)
        self.bt_log.setText(f"Pairing {mac}…")
        def _do():
            try:
                subprocess.run(['bluetoothctl','pair', mac], capture_output=True, timeout=15)
                subprocess.run(['bluetoothctl','trust', mac], capture_output=True, timeout=5)
                self.bt_log.setText(f"✅ Paired & trusted: {mac}")
            except Exception as e:
                self.bt_log.setText(f"❌ {e}")
        threading.Thread(target=_do, daemon=True).start()

    # WIFI extra
    def _disconnect_wifi(self):
        def _do():
            try:
                subprocess.run(['nmcli','dev','disconnect','wifi'], capture_output=True, timeout=8)
                self.wifi_log.setText(tr("wifi_ok").replace("✅ ", "🔌 Disconnected"))
            except Exception as e:
                self.wifi_log.setText(f"❌ {e}")
        threading.Thread(target=_do, daemon=True).start()

    def _forget_wifi(self):
        item = self.wifi_list.currentItem()
        if not item: return
        ssid = item.data(Qt.ItemDataRole.UserRole)
        def _do():
            try:
                subprocess.run(['nmcli','connection','delete', ssid], capture_output=True, timeout=8)
                self.wifi_log.setText(f"🗑 Forgotten: {ssid}")
            except Exception as e:
                self.wifi_log.setText(f"❌ {e}")
        threading.Thread(target=_do, daemon=True).start()

    # SIM
    def _scan_sim(self):
        self.sim_list.clear()
        self.sim_log.setText(tr("sim_scanning"))
        self.btn_scan_sim.setEnabled(False)
        self.ssw = SimScanWorker()
        self.ssw.done.connect(self._on_sim_done)
        self.ssw.error.connect(lambda e: (self.sim_log.setText(e), self.btn_scan_sim.setEnabled(True)))
        self.ssw.log.connect(lambda s: self.sim_log.setText(s))
        self.ssw.start()

    def _on_sim_done(self, modems):
        self.btn_scan_sim.setEnabled(True)
        if not modems:
            self.sim_log.setText(tr("sim_no_tool")); return
        self.sim_log.setText(tr("sim_found", len(modems)))
        for m in modems:
            txt = (f"📱 Modem {m['id']}  |  {tr('sim_operator', m['operator'])}  "
                   f"|  {tr('sim_signal', m['signal'])}  |  {tr('sim_state', m['state'])}  "
                   f"|  {m.get('tech','?')}")
            item = QListWidgetItem(txt)
            item.setData(Qt.ItemDataRole.UserRole, m['id'])
            self.sim_list.addItem(item)

    def _sim_enable(self):
        item = self.sim_list.currentItem()
        if not item: return
        idx = item.data(Qt.ItemDataRole.UserRole)
        def _do():
            try:
                subprocess.run(['mmcli','-m', idx,'--enable'], capture_output=True, timeout=10)
                self.sim_log.setText(f"✅ SIM {idx} enabled")
            except Exception as e:
                self.sim_log.setText(f"❌ {e}")
        threading.Thread(target=_do, daemon=True).start()

    def _sim_disable(self):
        item = self.sim_list.currentItem()
        if not item: return
        idx = item.data(Qt.ItemDataRole.UserRole)
        def _do():
            try:
                subprocess.run(['mmcli','-m', idx,'--disable'], capture_output=True, timeout=10)
                self.sim_log.setText(f"🔌 SIM {idx} disabled")
            except Exception as e:
                self.sim_log.setText(f"❌ {e}")
        threading.Thread(target=_do, daemon=True).start()

    # RETE
    def _refresh_net(self):
        self.net_list.clear()
        self.net_log.setText(tr("net_refresh") + "…")
        self.niw = NetIfaceWorker()
        self.niw.done.connect(self._on_net_done)
        self.niw.error.connect(lambda e: self.net_log.setText(f"❌ {e}"))
        self.niw.start()

    def _on_net_done(self, ifaces):
        self.net_log.setText("")
        for iface in ifaces:
            txt = (f"🔌 {iface['name']}  |  {tr('net_ip', iface['ip'])}  "
                   f"|  {tr('net_mac', iface['mac'])}  |  {tr('net_state', iface['state'])}")
            item = QListWidgetItem(txt)
            self.net_list.addItem(item)

    def _apply_dns(self):
        dns_text = self.dns_input.text().strip()
        if not dns_text: return
        dns_servers = [d.strip() for d in dns_text.replace(',', ' ').split() if d.strip()]
        def _do():
            try:
                # Applica DNS globale via nmcli (prima connessione attiva)
                out = subprocess.check_output(
                    ['nmcli','-t','-f','NAME,STATE','connection','show','--active'],
                    text=True, timeout=5, stderr=subprocess.DEVNULL)
                for line in out.strip().splitlines():
                    parts = line.split(':')
                    if len(parts) >= 2 and parts[1] == 'activated':
                        conn_name = parts[0]
                        dns_val = ','.join(dns_servers)
                        subprocess.run(['nmcli','con','mod', conn_name,
                                        'ipv4.dns', dns_val,
                                        'ipv4.ignore-auto-dns','yes'],
                                       capture_output=True, timeout=8)
                        subprocess.run(['nmcli','con','up', conn_name],
                                       capture_output=True, timeout=10)
                        self.net_log.setText(tr("net_dns_ok"))
                        return
                # Fallback: scrivi /etc/resolv.conf
                lines = '\n'.join(f'nameserver {d}' for d in dns_servers)
                subprocess.run(['sudo','tee','/etc/resolv.conf'],
                               input=lines, text=True, capture_output=True)
                self.net_log.setText(tr("net_dns_ok") + " (resolv.conf)")
            except Exception as e:
                self.net_log.setText(tr("net_dns_err", str(e)[:50]))
        threading.Thread(target=_do, daemon=True).start()

    # LINGUA
    def _change_language(self, lang_code):
        set_language(lang_code)
        # Aggiorna stili pulsanti lingua
        for code, btn in self._lang_btns.items():
            btn.setStyleSheet(self._lang_btn_style(code == lang_code))
        # Aggiorna UI dinamicamente
        self._refresh_ui_texts()

    def _refresh_ui_texts(self):
        """Aggiorna tutte le label/pulsanti con la nuova lingua."""
        # Status bar
        self.lbl_logo.setText("✦ " + tr("app_title").replace(" v2.3","").replace("LYRA OS","LYRA"))
        # Tab bar
        labels = [tr("tab_play"), tr("tab_search"), tr("tab_library"), tr("tab_system")]
        icons  = ["▶","⌕","♪","⚙"]
        for i, (b, lbl, ico) in enumerate(zip(self._tab_btns, labels, icons)):
            b.setText(f"{ico}  {lbl}")
        # Player tab
        if not self.current_file:
            self.lbl_title.setText(tr("no_track"))
            self.lbl_artist.setText("—")
        self.btn_rand.setText(tr("random"))
        self.btn_fwd.setText(tr("forward"))
        # Search tab
        self.search_input.setPlaceholderText(tr("search_placeholder"))
        self.search_status.setText(tr("search_ready"))
        # Library tab
        # System tab — sezioni (label sezione non dinamiche perché ricreate su tab switch, bastano i log)
        self.btn_scan_wifi.setText(tr("wifi_scan"))
        self.btn_wifi_disconnect.setText(tr("wifi_disconnect"))
        self.btn_wifi_forget.setText(tr("wifi_forget"))
        self.btn_scan_bt.setText(tr("bt_scan"))
        self.btn_bt_connect.setText(tr("bt_connect"))
        self.btn_bt_pair.setText(tr("bt_pair"))
        self.btn_scan_sim.setText(tr("sim_scan"))
        self.btn_sim_enable.setText(tr("sim_enable"))
        self.btn_sim_disable.setText(tr("sim_disable"))
        self.btn_net_refresh.setText(tr("net_refresh"))
        self.btn_reboot.setText(tr("btn_reboot"))
        self.btn_poweroff.setText(tr("btn_poweroff"))
        self.btn_exit_app.setText(tr("btn_exit"))
        self.lbl_batt_section.setText(tr("batt_title"))


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Forza dark palette di base per i dialog di sistema
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(C_BG))
    palette.setColor(palette.ColorRole.WindowText, QColor(C_TEXT))
    palette.setColor(palette.ColorRole.Base, QColor(C_SURF))
    palette.setColor(palette.ColorRole.Text, QColor(C_TEXT))
    palette.setColor(palette.ColorRole.Button, QColor(C_ELEV))
    palette.setColor(palette.ColorRole.ButtonText, QColor(C_TEXT))
    app.setPalette(palette)

    win = LyraOS()
    win.show()
    sys.exit(app.exec())