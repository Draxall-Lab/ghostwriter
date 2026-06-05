# Install Guide

This guide covers the basic installation steps for Ghostwriter for Obsidian.

At this stage, the guide assumes you already have Sapphire installed and working.

Later versions of this document will include the recommended Obsidian vault structure, `_meta` setup, and collaboration-zone guidance.

---

## 1. Open a Terminal

Open a terminal or command prompt on the machine where Sapphire is installed.

On Windows, this will usually be:

```text
Anaconda Prompt
```

or:

```text
PowerShell
```

On Linux, open your normal terminal.

---

## 2. Go to Your Sapphire Folder

Change into your Sapphire installation folder.

For example, on Linux this may be:

```bash
cd ~/sapphire
```

On Windows this may be something like:

```powershell
cd C:\Users\username\sapphire
```

Use the path that matches your own Sapphire installation.

---

## 3. Activate the Sapphire Conda Environment

Run:

```bash
conda activate sapphire
```

You should now see something like this at the start of your terminal line:

```text
(sapphire)
```

That means the Sapphire Python environment is active.

---

## 4. Install Plugin Requirements

From the Ghostwriter plugin folder, run:

```bash
pip install -r requirements.txt
```

If the plugin is inside your Sapphire user plugins folder, you may need to change into it first.

Example:

```bash
cd user/plugins/ghostwriter-for-obsidian
pip install -r requirements.txt
```

This installs any Python packages Ghostwriter needs.

---

## 5. Restart Sapphire

After installing the requirements, restart Sapphire so the plugin can load cleanly.

If you normally start Sapphire manually, stop it and run it again.

Example:

```bash
cd ~/sapphire
conda activate sapphire
python main.py
```

On Windows, use your own Sapphire path:

```powershell
cd C:\Users\username\sapphire
conda activate sapphire
python main.py
```

---

## 6. Enable the Plugin

Open Sapphire in your browser.

Go to:

```text
Settings → Plugins
```

Find Ghostwriter for Obsidian and enable it.

If the plugin is already enabled, disable and re-enable it after installing requirements.

---

## 7. Configure the Vault Path

Open the Ghostwriter plugin settings and set the path to your Obsidian vault.

The vault path should point to the root folder of the vault.

Example:

```text
E:\Obsidian\Test-Vault
```

or on Linux:

```text
/home/user/Obsidian/Test-Vault
```

---

## 8. Copy the contents of Vault-Content into your Obsidian vault root.

Ghostwriter does not create governance structure automatically.

The vault scaffold is intentional and forms part of the collaboration model.

## 9. Test the Connection

Ask Sapphire to check Ghostwriter’s vault status.

The plugin should confirm that the vault is reachable.

At this stage, do not continue until the vault status check succeeds.

---

## Current Notes

Ghostwriter is currently in early development.

The installation process may change as the plugin structure, meta-ops files, and recommended vault layout are finalised.

For now, the key setup steps are:

```bash
conda activate sapphire
pip install -r requirements.txt
```

Then restart Sapphire and configure the vault path.