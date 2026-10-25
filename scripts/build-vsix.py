#!/usr/bin/env python3
"""Build a .vsix for the Leylah Void theme using only the Python standard library.

Usage:  python3 scripts/build-vsix.py
Output: dist/leylah-void-<version>.vsix
"""
import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "package.json")) as fh:
    pkg = json.load(fh)

name = pkg["name"]
version = pkg["version"]
publisher = pkg["publisher"]
display = pkg["displayName"]
desc = pkg["description"]
engine = pkg["engines"]["vscode"]

manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="{name}" Version="{version}" Publisher="{publisher}" />
    <DisplayName>{display}</DisplayName>
    <Description xml:space="preserve">{desc}</Description>
    <Tags>{",".join(pkg.get("keywords", []))}</Tags>
    <Categories>Themes</Categories>
    <GalleryFlags>Public</GalleryFlags>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="{engine}" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionDependencies" Value="" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionPack" Value="" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="ui,workspace" />
      <Property Id="Microsoft.VisualStudio.Code.LocalizedLanguages" Value="" />
    </Properties>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code" />
  </Installation>
  <Dependencies />
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
  </Assets>
</PackageManifest>
"""

content_types = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="vsixmanifest" ContentType="text/xml" />
  <Default Extension="md" ContentType="text/markdown" />
  <Default Extension="png" ContentType="image/png" />
  <Default Extension="txt" ContentType="text/plain" />
</Types>
"""

files = [
    ("package.json", "extension/package.json"),
    ("themes/leylah-void-color-theme.json", "extension/themes/leylah-void-color-theme.json"),
    ("assets/icon.png", "extension/assets/icon.png"),
    ("README.md", "extension/README.md"),
    ("LICENSE", "extension/LICENSE"),
    ("CHANGELOG.md", "extension/CHANGELOG.md"),
]

dist = os.path.join(ROOT, "dist")
os.makedirs(dist, exist_ok=True)
out = os.path.join(dist, f"{name}-{version}.vsix")

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types)
    z.writestr("extension.vsixmanifest", manifest)
    for src, arc in files:
        path = os.path.join(ROOT, src)
        if os.path.exists(path):
            z.write(path, arc)

print(f"built {os.path.relpath(out, ROOT)} ({os.path.getsize(out)} bytes)")
