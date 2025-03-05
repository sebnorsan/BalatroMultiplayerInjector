import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import zipfile

# -----------------------------
# 1. Define Paths
# -----------------------------

# Game installation path
game_install_path = r"C:\Program Files (x86)\Steam\steamapps\common\Balatro"
version_dll_path = os.path.join(game_install_path, "version.dll")

# AppData Mods folder path
appdata = os.environ.get("APPDATA")
mods_path = os.path.join(appdata, "Balatro", "Mods")

# Expected mod folders inside Mods
expected_mods = ["BalatroMultiplayer", "SteamModded"]
mod_paths = {mod: os.path.join(mods_path, mod) for mod in expected_mods}

# Create a temporary hidden Tkinter root to show dialogs
temp_root = tk.Tk()
temp_root.withdraw()  # Hide the main window

# -----------------------------
# 2. Check for Missing Files & Folders
# -----------------------------

missing_items = []

# Check version.dll
if not os.path.exists(version_dll_path):
    missing_items.append("version.dll")

# Check Mods folder
if not os.path.exists(mods_path):
    missing_items.append("Mods folder")
else:
    # Check for missing mod folders
    for mod_name, path in mod_paths.items():
        if not os.path.exists(path):
            missing_items.append(mod_name)

# -----------------------------
# 3. Injection Process (if needed)
# -----------------------------

if missing_items:
    inject = messagebox.askyesno("Inject Balatro Multiplayer?", 
                                 "The following required items are missing:\n\n" +
                                 "\n".join(missing_items) +
                                 "\n\nWould you like to inject Balatro Multiplayer?"
                                 "\nSelect ZIP File")
    if inject:
        # Select ZIP File
        zip_path = filedialog.askopenfilename(title="Select Balatro Multiplayer ZIP File",
                                              filetypes=[("ZIP files", "*.zip")])
        if not zip_path:
            messagebox.showerror("Error", "No ZIP file selected. Proceeding without injection.")
        else:
            # Extract ZIP
            extract_path = os.path.join(os.path.dirname(zip_path), "Balatro_Temp_Extract")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract ZIP: {e}")
            else:
                # Check for nested folder (if only one item is extracted)
                extracted_items = os.listdir(extract_path)
                if len(extracted_items) == 1:
                    potential_nested_path = os.path.join(extract_path, extracted_items[0])
                    if os.path.isdir(potential_nested_path):
                        extract_path = potential_nested_path  # Adjust for nested structure

                # Move version.dll to Game Folder
                new_version_dll = os.path.join(extract_path, "version.dll")
                if not os.path.exists(new_version_dll):
                    messagebox.showerror("Error", "ZIP file is missing version.dll")
                elif not os.path.exists(game_install_path):
                    messagebox.showerror("Error", "Balatro is not installed. Please install it first.")
                else:
                    try:
                        shutil.copy2(new_version_dll, version_dll_path)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to copy version.dll: {e}")

                # Ensure Mods folder exists
                if not os.path.exists(mods_path):
                    os.makedirs(mods_path)

                # Remove old mod folders (including possible "-main" variants)
                old_mod_names = ["BalatroMultiplayer", "SteamModded", "BalatroMultiplayer-main", "smods-main"]
                for old_mod in old_mod_names:
                    old_mod_path = os.path.join(mods_path, old_mod)
                    if os.path.exists(old_mod_path):
                        try:
                            shutil.rmtree(old_mod_path)
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to remove old mod folder '{old_mod}': {e}")

                # Move new mod folders (if they exist in the ZIP)
                for mod_name in ["BalatroMultiplayer", "SteamModded"]:
                    extracted_mod_path = os.path.join(extract_path, mod_name)
                    if os.path.exists(extracted_mod_path):
                        try:
                            shutil.move(extracted_mod_path, os.path.join(mods_path, mod_name))
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to move '{mod_name}': {e}")

                # Clean up extracted files
                shutil.rmtree(os.path.join(os.path.dirname(zip_path), "Balatro_Temp_Extract"), ignore_errors=True)
                messagebox.showinfo("Success", "Injection complete. You can now use the mod manager.")
    else:
        messagebox.showinfo("Info", "Proceeding to Mod Manager without injection.")
else:
    messagebox.showinfo("Info", "All required files are present. Proceeding to Mod Manager.")

temp_root.destroy()

# -----------------------------
# 4. Set up the Mod Manager GUI
# -----------------------------

def list_mod_folders(mods_path):
    return [name for name in os.listdir(mods_path)
            if os.path.isdir(os.path.join(mods_path, name))]

def replace_mod_folder(mods_path, folder_name, new_folder_path):
    target_folder_path = os.path.join(mods_path, folder_name)
    try:
        shutil.rmtree(target_folder_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error deleting folder: {e}")
        return False
    try:
        shutil.copytree(new_folder_path, target_folder_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error copying folder: {e}")
        return False
    return True

def on_replace():
    selected_index = listbox.curselection()
    if not selected_index:
        messagebox.showinfo("Info", "Please select a folder to replace.")
        return
    folder_name = listbox.get(selected_index)
    new_folder_path = filedialog.askdirectory(title="Select New Folder")
    if not new_folder_path:
        return
    if replace_mod_folder(mods_path, folder_name, new_folder_path):
        messagebox.showinfo("Success", f"Replaced '{folder_name}' successfully.")
        refresh_list()

def on_add():
    new_mod_source = filedialog.askdirectory(title="Select New Mod Folder")
    if not new_mod_source:
        return
    new_mod_name = simpledialog.askstring("Folder Name", "Enter a name for the new mod folder:")
    if not new_mod_name:
        messagebox.showinfo("Info", "No name provided. Operation cancelled.")
        return
    new_mod_target = os.path.join(mods_path, new_mod_name)
    if os.path.exists(new_mod_target):
        messagebox.showerror("Error", f"A folder named '{new_mod_name}' already exists.")
        return
    try:
        shutil.copytree(new_mod_source, new_mod_target)
        messagebox.showinfo("Success", f"Added new mod folder '{new_mod_name}'.")
        refresh_list()
    except Exception as e:
        messagebox.showerror("Error", f"Error copying folder: {e}")

def on_remove():
    selected_index = listbox.curselection()
    if not selected_index:
        messagebox.showinfo("Info", "Please select a folder to remove.")
        return
    folder_name = listbox.get(selected_index)
    confirm = messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{folder_name}'?")
    if not confirm:
        return
    target_folder_path = os.path.join(mods_path, folder_name)
    try:
        shutil.rmtree(target_folder_path)
        messagebox.showinfo("Success", f"Removed '{folder_name}' successfully.")
        refresh_list()
    except Exception as e:
        messagebox.showerror("Error", f"Error removing folder: {e}")

def on_rename():
    selected_index = listbox.curselection()
    if not selected_index:
        messagebox.showinfo("Info", "Please select a folder to rename.")
        return
    old_mod_name = listbox.get(selected_index)
    new_mod_name = simpledialog.askstring("Folder Name", "Enter a new name for the mod folder:")
    if not new_mod_name:
        messagebox.showinfo("Info", "No name provided. Operation cancelled.")
        return
    old_folder_path = os.path.join(mods_path, old_mod_name)
    new_folder_path = os.path.join(mods_path, new_mod_name)
    if os.path.exists(new_folder_path):
        messagebox.showerror("Error", f"A folder named '{new_mod_name}' already exists.")
        return
    try:
        os.rename(old_folder_path, new_folder_path)
        messagebox.showinfo("Success", f"Folder renamed to '{new_mod_name}' successfully.")
        refresh_list()
    except Exception as e:
        messagebox.showerror("Error", f"Error renaming folder: {e}")

def refresh_list():
    listbox.delete(0, tk.END)
    folders = list_mod_folders(mods_path)
    for folder in folders:
        listbox.insert(tk.END, folder)

# Create the main Tkinter window for the mod manager
root = tk.Tk()
root.title("Mod Folder Manager")

listbox = tk.Listbox(root, width=50)
listbox.pack(padx=10, pady=10)

replace_button = tk.Button(root, text="Replace Selected Folder", command=on_replace)
replace_button.pack(padx=10, pady=(0,10))

add_button = tk.Button(root, text="Add New Folder", command=on_add)
add_button.pack(padx=10, pady=(0,10))

remove_button = tk.Button(root, text="Remove Selected Folder", command=on_remove)
remove_button.pack(padx=10, pady=(0,10))

rename_button = tk.Button(root, text="Rename Selected Folder", command=on_rename)
rename_button.pack(padx=10, pady=(0,10))

refresh_list()

root.mainloop()
