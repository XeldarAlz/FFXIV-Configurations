import os
import sys
import shutil
import winreg
import threading
from pathlib import Path
from typing import Optional
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FFXIVConfigInstaller(ctk.CTk):
    
    COMMON_PATHS = [
        r"C:\Program Files (x86)\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
        r"C:\Program Files\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
        r"D:\Games\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
        r"D:\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
        r"E:\Games\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
        r"C:\Games\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
    ]
    
    STEAM_PATHS = [
        r"C:\Program Files (x86)\Steam\steamapps\common\FINAL FANTASY XIV Online",
        r"C:\Program Files\Steam\steamapps\common\FINAL FANTASY XIV Online",
        r"D:\Steam\steamapps\common\FINAL FANTASY XIV Online",
        r"D:\SteamLibrary\steamapps\common\FINAL FANTASY XIV Online",
        r"E:\SteamLibrary\steamapps\common\FINAL FANTASY XIV Online",
    ]

    def __init__(self):
        super().__init__()
        
        self.title("Xeldar FFXIV Configs")
        self.geometry("600x1100")
        self.minsize(100, 105)
        
        if getattr(sys, 'frozen', False):
            self.app_dir = Path(sys._MEIPASS)
            self.icon_path = Path(sys._MEIPASS) / "X.ico"
        else:
            self.app_dir = Path(__file__).parent.parent
            self.icon_path = Path(__file__).parent / "X.ico"
        
        if self.icon_path.exists():
            self.iconbitmap(str(self.icon_path))
        
        self.skills_source = self.app_dir / "Mods Configs" / "Skills"
        self.reshade_presets_source = self.app_dir / "ReShade Configs" / "reshade-presets"
        self.reshade_shaders_source = self.app_dir / "ReShade Configs" / "reshade-shaders"
        self.ffxiv_config_source = self.app_dir / "FFXIV Configs" / "FINAL FANTASY XIV - A Realm Reborn"
        self.plugin_configs_source = self.app_dir / "XIVLauncher Configs" / "Plugins" / "pluginConfigs"
        
        self.game_path: Optional[Path] = None
        self.documents_path = Path(os.path.expanduser("~")) / "Documents" / "My Games"
        self.appdata_path = Path(os.environ.get("APPDATA", "")) / "XIVLauncher"
        
        self._create_ui()
        self._auto_detect_game()
    
    def _create_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._create_header()
        self._create_path_section()
        self._create_options_section()
        self._create_progress_section()
        self._create_action_buttons()
    
    def _create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="#1a1a2e", corner_radius=12)
        header_frame.pack(fill="x", pady=(0, 15))
        
        top_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_row.pack(fill="x", padx=15, pady=(10, 0))
        
        try:
            from PIL import Image
            if self.icon_path.exists():
                icon_image = Image.open(str(self.icon_path))
                icon_ctk = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(48, 48))
                icon_label = ctk.CTkLabel(top_row, image=icon_ctk, text="")
                icon_label.pack(side="left", padx=(5, 10))
        except ImportError:
            pass
        
        dev_label = ctk.CTkLabel(
            top_row,
            text="developed by Xeldar",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#64ffda"
        )
        dev_label.pack(side="right", padx=5)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚔️  Xeldar FFXIV Configs  ⚔️",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#e6b422"
        )
        title_label.pack(pady=(5, 5))
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Automate FFXIV configuration setup",
            font=ctk.CTkFont(size=13),
            text_color="#8892b0"
        )
        subtitle_label.pack(pady=(0, 15))
    
    def _create_path_section(self):
        path_frame = ctk.CTkFrame(self.main_frame, fg_color="#16213e", corner_radius=10)
        path_frame.pack(fill="x", pady=(0, 15))
        
        section_label = ctk.CTkLabel(
            path_frame,
            text="📁 Path Configuration",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#64ffda"
        )
        section_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        game_path_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        game_path_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            game_path_frame,
            text="FFXIV Game Directory:",
            font=ctk.CTkFont(size=12),
            text_color="#ccd6f6"
        ).pack(anchor="w")
        
        path_input_frame = ctk.CTkFrame(game_path_frame, fg_color="transparent")
        path_input_frame.pack(fill="x", pady=(5, 0))
        
        self.game_path_entry = ctk.CTkEntry(
            path_input_frame,
            placeholder_text="Select or auto-detect FFXIV installation...",
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.game_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            path_input_frame,
            text="Browse",
            width=80,
            height=35,
            command=self._browse_game_path,
            fg_color="#0f3460",
            hover_color="#1a508b"
        )
        browse_btn.pack(side="left", padx=(0, 5))
        
        detect_btn = ctk.CTkButton(
            path_input_frame,
            text="Auto-Detect",
            width=100,
            height=35,
            command=self._auto_detect_game,
            fg_color="#533483",
            hover_color="#6b4299"
        )
        detect_btn.pack(side="left")
        
        self.path_status_label = ctk.CTkLabel(
            path_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#8892b0"
        )
        self.path_status_label.pack(anchor="w", padx=15, pady=(5, 15))
    
    def _create_options_section(self):
        options_frame = ctk.CTkFrame(self.main_frame, fg_color="#16213e", corner_radius=10)
        options_frame.pack(fill="x", pady=(0, 15))
        
        section_label = ctk.CTkLabel(
            options_frame,
            text="⚙️ Installation Options",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#64ffda"
        )
        section_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        self.install_skills_var = ctk.BooleanVar(value=True)
        self.install_reshade_var = ctk.BooleanVar(value=True)
        self.install_config_var = ctk.BooleanVar(value=True)
        self.install_plugins_var = ctk.BooleanVar(value=True)
        
        skills_check = ctk.CTkCheckBox(
            options_frame,
            text="Install Skill Mods (copy to game directory for Penumbra)",
            variable=self.install_skills_var,
            font=ctk.CTkFont(size=13),
            text_color="#ccd6f6",
            fg_color="#e6b422",
            hover_color="#d4a41f"
        )
        skills_check.pack(anchor="w", padx=20, pady=5)
        
        skills_desc = ctk.CTkLabel(
            options_frame,
            text="    → Copies Skills folder to game directory",
            font=ctk.CTkFont(size=11),
            text_color="#8892b0"
        )
        skills_desc.pack(anchor="w", padx=20)
        
        reshade_check = ctk.CTkCheckBox(
            options_frame,
            text="Install ReShade Presets & Shaders",
            variable=self.install_reshade_var,
            font=ctk.CTkFont(size=13),
            text_color="#ccd6f6",
            fg_color="#e6b422",
            hover_color="#d4a41f"
        )
        reshade_check.pack(anchor="w", padx=20, pady=(10, 5))
        
        reshade_desc = ctk.CTkLabel(
            options_frame,
            text="    → Copies reshade-presets and reshade-shaders to game folder",
            font=ctk.CTkFont(size=11),
            text_color="#8892b0"
        )
        reshade_desc.pack(anchor="w", padx=20)
        
        config_check = ctk.CTkCheckBox(
            options_frame,
            text="Install FFXIV Configuration Files",
            variable=self.install_config_var,
            font=ctk.CTkFont(size=13),
            text_color="#ccd6f6",
            fg_color="#e6b422",
            hover_color="#d4a41f"
        )
        config_check.pack(anchor="w", padx=20, pady=(10, 5))
        
        config_desc = ctk.CTkLabel(
            options_frame,
            text="    → Copies FFXIV settings to Documents\\My Games",
            font=ctk.CTkFont(size=11),
            text_color="#8892b0"
        )
        config_desc.pack(anchor="w", padx=20)
        
        plugins_check = ctk.CTkCheckBox(
            options_frame,
            text="Install XIVLauncher Plugin Configs",
            variable=self.install_plugins_var,
            font=ctk.CTkFont(size=13),
            text_color="#ccd6f6",
            fg_color="#e6b422",
            hover_color="#d4a41f"
        )
        plugins_check.pack(anchor="w", padx=20, pady=(10, 5))
        
        plugins_desc = ctk.CTkLabel(
            options_frame,
            text="    → Copies pluginConfigs to AppData\\Roaming\\XIVLauncher",
            font=ctk.CTkFont(size=11),
            text_color="#8892b0"
        )
        plugins_desc.pack(anchor="w", padx=20, pady=(0, 15))
    
    def _create_progress_section(self):
        progress_frame = ctk.CTkFrame(self.main_frame, fg_color="#16213e", corner_radius=10)
        progress_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        section_label = ctk.CTkLabel(
            progress_frame,
            text="📋 Progress Log",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#64ffda"
        )
        section_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        self.progress_text = ctk.CTkTextbox(
            progress_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0a0a0f",
            text_color="#a8b2d1",
            corner_radius=8
        )
        self.progress_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            progress_color="#e6b422",
            fg_color="#1a1a2e"
        )
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 15))
        self.progress_bar.set(0)
    
    def _create_action_buttons(self):
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        self.install_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Install Configurations",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color="#e6b422",
            hover_color="#d4a41f",
            text_color="#1a1a2e",
            command=self._start_installation
        )
        self.install_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        exit_btn = ctk.CTkButton(
            button_frame,
            text="Exit",
            font=ctk.CTkFont(size=14),
            height=45,
            width=100,
            fg_color="#c23a22",
            hover_color="#a83219",
            command=self.quit
        )
        exit_btn.pack(side="right")
    
    def _log(self, message: str, tag: str = "info"):
        prefix_map = {
            "info": "ℹ️ ",
            "success": "✅ ",
            "error": "❌ ",
            "warning": "⚠️ ",
            "progress": "⏳ "
        }
        prefix = prefix_map.get(tag, "")
        self.progress_text.insert("end", f"{prefix}{message}\n")
        self.progress_text.see("end")
        self.update_idletasks()
    
    def _clear_log(self):
        self.progress_text.delete("1.0", "end")
    
    def _auto_detect_game(self):
        self._log("Searching for FFXIV installation...", "progress")
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 39210"
            )
            install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)
            if Path(install_path).exists():
                self._set_game_path(Path(install_path))
                return
        except (WindowsError, FileNotFoundError):
            pass
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{2B41E132-07DF-4925-A3D3-F2D1765CBER7}_is1"
            )
            install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)
            if Path(install_path).exists():
                self._set_game_path(Path(install_path))
                return
        except (WindowsError, FileNotFoundError):
            pass
        
        all_paths = self.COMMON_PATHS + self.STEAM_PATHS
        for path_str in all_paths:
            path = Path(path_str)
            if path.exists() and (path / "game").exists():
                self._set_game_path(path)
                return
        
        self._log("Could not auto-detect FFXIV. Please browse manually.", "warning")
        self.path_status_label.configure(
            text="⚠️ FFXIV not found. Please select manually.",
            text_color="#f0a500"
        )
    
    def _browse_game_path(self):
        folder = filedialog.askdirectory(
            title="Select FFXIV Installation Directory",
            initialdir="C:\\Program Files (x86)"
        )
        if folder:
            self._set_game_path(Path(folder))
    
    def _set_game_path(self, path: Path):
        self.game_path = path
        self.game_path_entry.delete(0, "end")
        self.game_path_entry.insert(0, str(path))
        
        game_folder = path / "game"
        if game_folder.exists():
            self._log(f"Found FFXIV at: {path}", "success")
            self.path_status_label.configure(
                text=f"✅ Valid FFXIV installation detected",
                text_color="#64ffda"
            )
        else:
            self._log(f"Warning: 'game' subfolder not found at {path}", "warning")
            self.path_status_label.configure(
                text="⚠️ 'game' folder not found - may not be valid FFXIV path",
                text_color="#f0a500"
            )
    
    def _start_installation(self):
        game_path_str = self.game_path_entry.get().strip()
        if not game_path_str:
            messagebox.showerror("Error", "Please select the FFXIV game directory first.")
            return
        
        self.game_path = Path(game_path_str)
        if not self.game_path.exists():
            messagebox.showerror("Error", f"The selected path does not exist:\n{self.game_path}")
            return
        
        if not any([
            self.install_skills_var.get(),
            self.install_reshade_var.get(),
            self.install_config_var.get(),
            self.install_plugins_var.get()
        ]):
            messagebox.showwarning("Warning", "Please select at least one installation option.")
            return
        
        self.install_btn.configure(state="disabled", text="Installing...")
        self._clear_log()
        self.progress_bar.set(0)
        
        thread = threading.Thread(target=self._run_installation, daemon=True)
        thread.start()
    
    def _run_installation(self):
        try:
            total_steps = sum([
                self.install_skills_var.get(),
                self.install_reshade_var.get(),
                self.install_config_var.get(),
                self.install_plugins_var.get()
            ])
            current_step = 0
            
            self._log("Starting installation process...", "info")
            self._log(f"Game directory: {self.game_path}", "info")
            self._log("-" * 50, "info")
            
            if self.install_skills_var.get():
                self._install_skills()
                current_step += 1
                self.progress_bar.set(current_step / total_steps)
            
            if self.install_reshade_var.get():
                self._install_reshade()
                current_step += 1
                self.progress_bar.set(current_step / total_steps)
            
            if self.install_config_var.get():
                self._install_ffxiv_config()
                current_step += 1
                self.progress_bar.set(current_step / total_steps)
            
            if self.install_plugins_var.get():
                self._install_plugin_configs()
                current_step += 1
                self.progress_bar.set(current_step / total_steps)
            
            self._log("-" * 50, "info")
            self._log("Installation completed successfully!", "success")
            self._log("", "info")
            self._log("Next steps:", "info")
            if self.install_skills_var.get():
                self._log("  • Open Penumbra and import the skill mods", "info")
            if self.install_reshade_var.get():
                self._log("  • Configure ReShade to use the installed presets", "info")
            
            self.after(0, lambda: messagebox.showinfo(
                "Success",
                "Configuration installation completed!\n\nCheck the progress log for details."
            ))
            
        except Exception as e:
            self._log(f"Installation failed: {str(e)}", "error")
            self.after(0, lambda: messagebox.showerror("Error", f"Installation failed:\n{str(e)}"))
        
        finally:
            self.after(0, lambda: self.install_btn.configure(
                state="normal",
                text="🚀 Install Configurations"
            ))
    
    def _install_skills(self):
        self._log("Installing Skill Mods...", "progress")
        
        if not self.skills_source.exists():
            self._log(f"Skills source not found: {self.skills_source}", "error")
            return
        
        dest = self.game_path / "Skills"
        self._copy_folder(self.skills_source, dest)
        self._log(f"Skills mods copied to: {dest}", "success")
    
    def _install_reshade(self):
        self._log("Installing ReShade files...", "progress")
        
        game_folder = self.game_path / "game"
        if not game_folder.exists():
            game_folder = self.game_path
        
        if self.reshade_presets_source.exists():
            dest_presets = game_folder / "reshade-presets"
            self._copy_folder(self.reshade_presets_source, dest_presets)
            self._log(f"ReShade presets copied to: {dest_presets}", "success")
        else:
            self._log(f"ReShade presets source not found: {self.reshade_presets_source}", "warning")
        
        if self.reshade_shaders_source.exists():
            dest_shaders = game_folder / "reshade-shaders"
            self._copy_folder(self.reshade_shaders_source, dest_shaders)
            self._log(f"ReShade shaders copied to: {dest_shaders}", "success")
        else:
            self._log(f"ReShade shaders source not found: {self.reshade_shaders_source}", "warning")
    
    def _install_ffxiv_config(self):
        self._log("Installing FFXIV configuration files...", "progress")
        
        if not self.ffxiv_config_source.exists():
            self._log(f"FFXIV config source not found: {self.ffxiv_config_source}", "error")
            return
        
        self.documents_path.mkdir(parents=True, exist_ok=True)
        
        dest = self.documents_path / "FINAL FANTASY XIV - A Realm Reborn"
        
        if dest.exists():
            backup_path = self.documents_path / "FINAL FANTASY XIV - A Realm Reborn.backup"
            if backup_path.exists():
                shutil.rmtree(backup_path)
            self._log(f"Backing up existing config to: {backup_path}", "info")
            shutil.move(str(dest), str(backup_path))
        
        self._copy_folder(self.ffxiv_config_source, dest)
        self._log(f"FFXIV configuration copied to: {dest}", "success")
    
    def _install_plugin_configs(self):
        self._log("Installing XIVLauncher plugin configs...", "progress")
        
        if not self.plugin_configs_source.exists():
            self._log(f"Plugin configs source not found: {self.plugin_configs_source}", "error")
            return
        
        self.appdata_path.mkdir(parents=True, exist_ok=True)
        
        dest = self.appdata_path / "pluginConfigs"
        
        if dest.exists():
            backup_path = self.appdata_path / "pluginConfigs.backup"
            if backup_path.exists():
                shutil.rmtree(backup_path)
            self._log(f"Backing up existing plugin configs to: {backup_path}", "info")
            shutil.move(str(dest), str(backup_path))
        
        self._copy_folder(self.plugin_configs_source, dest)
        self._log(f"Plugin configs copied to: {dest}", "success")
    
    def _copy_folder(self, src: Path, dest: Path):
        if dest.exists():
            self._log(f"Removing existing: {dest.name}", "info")
            shutil.rmtree(dest)
        
        self._log(f"Copying: {src.name} → {dest.parent.name}/", "info")
        shutil.copytree(str(src), str(dest))


def main():
    app = FFXIVConfigInstaller()
    app.mainloop()


if __name__ == "__main__":
    main()
