bl_info = {
    "name": "B SubEditor",
    "author": "Dinesh",
    "version": (1, 0, 0),
    "blender": (2, 8, 0),
    "location": "VSE/Text Editor > Import/ExportSubtitle",
    "description": "Sync subtitles in Text Editor/VSE",
    "category": "Text Editor, Sequencer, Import/Export",
}

import bpy
import os
import re
from datetime import datetime

def read_subtitle_file(file_path):
    """Reads subtitle file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def write_subtitle_file(file_path, content):
    """Writes content to a subtitle file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

def ensure_unique_filepath(base_path, extension):
    """Generates a unique file path by appending a numerical suffix if needed."""
    counter = 1
    unique_path = f"{base_path}{extension}"
    while os.path.exists(unique_path):
        unique_path = f"{base_path}_{counter:03d}{extension}"
        counter += 1
    return unique_path

def convert_to_srt(content, format):
    """Converts the given subtitle content to SRT format."""
    if format == 'TXT':
        lines = content.splitlines()
        srt_content = []
        for i, line in enumerate(lines, start=1):
            if line.strip():
                start_time = f"00:00:{(i - 1) * 3 + 1:02},000"
                end_time = f"00:00:{(i - 1) * 3 + 3:02},000"
                srt_content.append(f"{i}\n{start_time} --> {end_time}\n{line.strip()}\n")
        return "\n".join(srt_content)
    return content

def convert_from_srt(content, format):
    """Converts the given SRT content to the specified format."""
    if format == 'VTT':
        return "WEBVTT\n\n" + content.replace(",", ".")
    elif format == 'SBV':
        return "\n".join([line.replace(",", "") for line in content.splitlines() if line])
    return content

class SUBTITLE_OT_import(bpy.types.Operator):
    """Import subtitles into Text Editor"""
    bl_idname = "subtitle.import"
    bl_label = "Import Subtitle"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.srt;*.vtt;*.sbv;*.txt",
        options={'HIDDEN'},
    )

    def execute(self, context):
        content = read_subtitle_file(self.filepath)
        if content:
            ext = os.path.splitext(self.filepath)[1].lower()
            format = 'TXT' if ext == '.txt' else ext[1:].upper()
            if format != 'SRT':
                content = convert_to_srt(content, format)

            text_block = bpy.data.texts.new(name=os.path.basename(self.filepath))
            text_block.from_string(content)
            self.report({'INFO'}, f"Imported subtitle: {self.filepath}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to import subtitle")
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Support: STR, VTT, SBV, TXT", icon='DOCUMENTS')


class SUBTITLE_OT_export(bpy.types.Operator):
    """Export Text Editor content as subtitle"""
    bl_idname = "subtitle.export"
    bl_label = "Export Subtitle"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.*",
        options={'HIDDEN'},
    )
    format: bpy.props.EnumProperty(
        name="Format",
        description="Select subtitle format",
        items=[
            ('SRT', "SRT (.srt)", "SubRip Subtitle format"),
            ('VTT', "VTT (.vtt)", "WebVTT format"),
            ('SBV', "SBV (.sbv)", "YouTube Subtitle format"),
        ],
        default='SRT',
    )

    def execute(self, context):
        active_text = context.space_data.text
        if not active_text:
            self.report({'ERROR'}, "No active text to export")
            return {'CANCELLED'}

        # Extract base path and extension
        base_path, _ = os.path.splitext(self.filepath)
        extension = f".{self.format.lower()}"

        # Ensure the file path is unique
        unique_path = ensure_unique_filepath(base_path, extension)

        content = active_text.as_string()
        if self.format != 'SRT':
            content = convert_from_srt(content, self.format)

        success = write_subtitle_file(unique_path, content)
        if success:
            self.report({'INFO'}, f"Exported subtitle to: {unique_path}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to export subtitle")
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "format", text="Subtitle Format", icon='FILE_CACHE')
        

def menu_func_sub(self, context):
    layout = self.layout
    layout.separator()

    st = context.space_data
    text = st.text

    layout.operator(SUBTITLE_OT_import.bl_idname, text="Import Subtitle", icon='IMPORT')
    if text:
        layout.operator(SUBTITLE_OT_export.bl_idname, text="Export Subtitle", icon='EXPORT')


# Footer panel for displaying text info
class TEXT_HT_footer(bpy.types.Header):
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'FOOTER'

    def draw(self, context):
        layout = self.layout
        st = context.space_data
        text = st.text
        settings = context.scene.text_info_settings  # Access settings

        if text:
            row = layout.row()
            # File or Text Info
            if text.filepath:
                row.label(text=f"File: *(Unsaved)" if text.is_dirty else "File: (Saved)")
            else:
                row.label(text="Text: External" if text.library else "Text: Internal")

            # Total Lines
            row.label(text=f"Lns: {len(text.lines)}")

            # Spacer
            row.separator_spacer()

            # Cursor Position
            cursor_line = text.current_line_index + 1
            cursor_column = text.current_character + 1  # Blender uses zero-based indices
            row.label(text=f"Ln {cursor_line}, Col {cursor_column}")

            # Selected Characters
            if text.select_end_line_index >= 0:
                start_line_index = min(text.current_line_index, text.select_end_line_index)
                end_line_index = max(text.current_line_index, text.select_end_line_index)
                start_character = min(text.current_character, text.select_end_character)
                end_character = max(text.current_character, text.select_end_character)

                selected_count = 0
                for i in range(start_line_index, end_line_index + 1):
                    line = text.lines[i].body
                    if i == start_line_index and i == end_line_index:
                        selected_text = line[start_character:end_character]
                    elif i == start_line_index:
                        selected_text = line[start_character:]
                    elif i == end_line_index:
                        selected_text = line[:end_character]
                    else:
                        selected_text = line

                    # Add the length of selected text, excluding spaces if unchecked
                    if settings.count_spaces:
                        selected_count += len(selected_text)
                    else:
                        selected_count += len(selected_text.replace(" ", ""))

                row.label(text=f"({selected_count} Selected)")
            else:
                row.label(text="")

            # Indentation Spaces
            current_line = text.current_line.body
            indentation_spaces = len(current_line) - len(current_line.lstrip())
            row.label(text=f"Spaces: {indentation_spaces}")

        else:
            layout.separator_spacer()
            layout.label(text="----- Text Info -----")
            layout.separator_spacer()

# Add a property to store whether spaces should be counted
class TextInfoSettings(bpy.types.PropertyGroup):
    count_spaces: bpy.props.BoolProperty(
        name="Selected Count Spaces",
        description="Include spaces in selected character count",
        default=True
    )

# Text Panel with Count Spaces Checkbox
class TEXT_Pannel(bpy.types.Panel):
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Text"
    bl_label = "Text Info"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.text_info_settings  # Access settings
        
        # Checkbox for toggling space counting
        row = layout.row()
        row.prop(settings, "count_spaces")

# ----------------------- Subtitle VSE------------------------

# Parse color string to Blender-compatible RGBA tuple
def parse_color(color_string):
    """Convert a color string (name or hex) to a Blender-compatible color tuple."""
    try:
        if color_string.startswith("#"):
            hex_color = color_string.lstrip("#")
            rgb = tuple(int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))
            return (*rgb, 1.0)
        else:
            color_dict = {
                "red": (1.0, 0.0, 0.0, 1.0),
                "green": (0.0, 1.0, 0.0, 1.0),
                "blue": (0.0, 0.0, 1.0, 1.0),
                "black": (0.0, 0.0, 0.0, 1.0),
                "yellow": (1.0, 1.0, 0.0, 1.0),
                "cyan": (0.0, 1.0, 1.0, 1.0),
                "magenta": (1.0, 0.0, 1.0, 1.0),
                "white": (1.0, 1.0, 1.0, 1.0),
            }
            return color_dict.get(color_string.lower(), (1.0, 1.0, 1.0, 1.0))
    except Exception:
        return (1.0, 1.0, 1.0, 1.0)
    
def parse_srt_data(content):
    """Parse SRT content and return a list of (start, end, text, styles)."""
    pattern = (
        r"(\d+)\n"  # Index
        r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n"  # Timecodes
        r"(.*?)(?:\n\n|\Z)"  # Text
    )
    matches = re.findall(pattern, content, re.DOTALL)

    subtitles = []
    for _, start, end, text in matches:
        # Ignore lines starting with '#' or enclosed within '<!-- -->'
        lines = text.splitlines()
        filtered_lines = [
            line for line in lines
            if not line.strip().startswith("#") and not re.match(r"<!--.*?-->", line.strip())
        ]
        filtered_text = "\n".join(filtered_lines).strip()

        # Skip empty subtitle blocks
        if not filtered_text:
            continue

        start_seconds = timecode_to_seconds(start)
        end_seconds = timecode_to_seconds(end)

        # Process styles
        filtered_text, styles = process_srt_styles(filtered_text)

        subtitles.append((start_seconds, end_seconds, filtered_text, styles))

    return subtitles


def timecode_to_seconds(timecode):
    """Convert SRT-style timecode (HH:MM:SS,MS) to seconds."""
    h, m, s_ms = timecode.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


# Process SRT styles
def process_srt_styles(text):
    """Extract and map SRT styles to Blender text strip styles."""
    styles = {
        "use_bold": "<b>" in text,
        "use_italic": "<i>" in text,
        "use_box": "<u>" in text,  # Map underline to use_box for visibility
        "font_size": 40,  # Default font size
        "color": "",  # Default color
        "wrap_width": 0.8,
        "location[1]": 0.15,
    }

    # Extract font size and color
    font_size_match = re.search(r'size="(\d+)"', text)
    color_match = re.search(r'color="(#[0-9A-Fa-f]{6}|[a-zA-Z]+)"', text)

    if font_size_match:
        styles["font_size"] = int(font_size_match.group(1))
    if color_match:
        styles["color"] = color_match.group(1)

    # Remove SRT tags
    clean_text = re.sub(r"<.*?>", "", text)
    clean_text = clean_text.replace("\\n", "\n").replace("<br>", "\n")

    return clean_text.strip(), styles


def create_text_strips(context, subtitles, channel):
    """Add text strips to the VSE based on subtitle timings and styles."""
    scene = context.scene
    sequencer = scene.sequence_editor

    if not sequencer:
        scene.sequence_editor_create()

    # Deselect all existing strips
    for strip in sequencer.sequences_all:
        strip.select = False 

    for start, end, text, styles in subtitles:
        start_frame = int(start * scene.render.fps)
        end_frame = int(end * scene.render.fps)

        # Create the text strip
        text_strip = sequencer.sequences.new_effect(
            name=text[:15],
            type='TEXT',
            channel=channel,
            frame_start=start_frame,
            frame_end=end_frame,
        )

        # Assign text content and styles
        text_strip.text = text
        text_strip.use_bold = styles["use_bold"]
        text_strip.use_italic = styles["use_italic"]
        text_strip.use_box = styles["use_box"]
        text_strip.font_size = styles["font_size"]
        text_strip.color = parse_color(styles["color"])
        text_strip.wrap_width = styles["wrap_width"]
        text_strip.location[1] = styles["location[1]"]


def export_selected_text_strips_to_text_editor(context):
    """Export selected text strips from the VSE to the Text Editor as SRT format."""
    scene = context.scene
    sequencer = scene.sequence_editor

    if not sequencer:
        return "No VSE sequences found to export."

    strips = [s for s in sequencer.sequences_all if s.type == 'TEXT' and s.select]
    if not strips:
        return "No selected text strips found to export."

    # Generate metadata
    metadata = (
        f"# Metadata\n"
        f"# Title: Subtitles\n"
        f"# Author: Your Name\n"
        f"# Tags: Comedy,\n"
        f"# Language: English\n"
        f"# Encoding: UTF-8\n"
        f"# Created: {datetime.now().strftime('%Y-%m-%d')}\n"
        f"# Tool: Blender\n\n"
    )

    # Create an SRT-formatted string
    srt_content = metadata
    for index, strip in enumerate(strips, 1):
        start_seconds = strip.frame_start / scene.render.fps
        end_seconds = strip.frame_final_end / scene.render.fps
        start_timecode = seconds_to_timecode(start_seconds)
        end_timecode = seconds_to_timecode(end_seconds)

        # Convert Blender styles to SRT tags
        text = strip.text
        if getattr(strip, "use_bold", False):
            text = f"<b>{text}</b>"
        if getattr(strip, "use_italic", False):
            text = f"<i>{text}</i>"
        if getattr(strip, "use_box", False):  # Represent box as underline
            text = f"<u>{text}</u>"

        # Skip exporting font size if it is default
        if getattr(strip, "font_size", 40) != 40:
            text = f'<font size="{strip.font_size}">{text}</font>'
            
        # Remove name prefix if present
        text = re.sub(r"^\[.*?\]:", "", text).strip()

        # Replace newline characters for multi-line text
        text = text.replace("\n", "\\n")

        # Include the name prefix if available
        name_prefix = strip.name.split(" ")[0] if "[" in strip.name else ""
        if name_prefix:
            text = f"{name_prefix} {text}"

        # Skip exporting the color tag if the color is default white
        color_hex = "".join(f"{int(c * 255):02X}" for c in strip.color[:3])
        if color_hex.upper() != "FFFFFF":
            text = f'<font color="#{color_hex}">{text}</font>'

        srt_content += f"{index}\n{start_timecode} --> {end_timecode}\n{text}\n\n"

    # Generate a unique name for the text block
    base_name = "Subtitles_Export"
    existing_names = [text.name for text in bpy.data.texts]
    counter = 1
    while f"{base_name}_{counter:03}" in existing_names:
        counter += 1
    text_block_name = f"{base_name}_{counter:03}"

    # Add a new Text block in the Text Editor
    text_block = bpy.data.texts.new(text_block_name)
    text_block.write(srt_content)

    return f"Exported {len(strips)} selected subtitles to '{text_block_name}'."

def seconds_to_timecode(seconds):
    """Convert seconds to SRT timecode (HH:MM:SS,MS)."""
    ms = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    s = seconds % 60
    m = (seconds // 60) % 60
    h = seconds // 3600
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# ----------------------- Operators ------------------------

class VSEImportSubtitlesOperator(bpy.types.Operator):
    """Import subtitles into VSE from Text Editor"""
    bl_idname = "vse.import_subtitles"
    bl_label = "Import Subtitles from Text Editor"
    bl_options = {'REGISTER', 'UNDO'}

    channel: bpy.props.IntProperty(name="Channel", default=2, min=1, max=128)
    text_block_name: bpy.props.StringProperty(name="Text Block Name")
    toggle_connect: bpy.props.BoolProperty(
        name="Connect Strips",
        default=True,
        description="Connect created subtitle strips"
    )

    def execute(self, context):
        text_block = bpy.data.texts.get(self.text_block_name)
        if not text_block:
            self.report({'ERROR'}, f"No text block named '{self.text_block_name}' found.")
            return {'CANCELLED'}

        subtitles = parse_srt_data(text_block.as_string())
        if not subtitles:
            self.report({'WARNING'}, "No valid subtitles found in the text block.")
            return {'CANCELLED'}

        create_text_strips(context, subtitles, self.channel)

        # Handle toggling connection
        if self.toggle_connect:
            bpy.ops.sequencer.connect(toggle=True)
        else:
            bpy.ops.sequencer.disconnect()

        self.report({'INFO'}, f"Imported {len(subtitles)} subtitles into VSE.")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "text_block_name", bpy.data, "texts", text="Text Block")
        layout.prop(self, "channel", text="Target Channel")
        layout.prop(self, "toggle_connect", text="Connect Strips")


class VSEExportSubtitlesOperator(bpy.types.Operator):
    """Export selected subtitles from VSE to Text Editor"""
    bl_idname = "vse.export_subtitles"
    bl_label = "Export Subtitles to Text Editor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        result = export_selected_text_strips_to_text_editor(context)
        self.report({'INFO'}, result)
        return {'FINISHED'}

class VSE_MT_subtitle_menu(bpy.types.Menu):
    """Subtitles Menu for VSE"""
    bl_label = "Subtitles"
    bl_idname = "VSE_MT_subtitle_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("vse.import_subtitles", text="Import Subtitles", icon='TRACKING_REFINE_BACKWARDS')
        layout.operator("vse.export_subtitles", text="Export Subtitles", icon='TRACKING_REFINE_FORWARDS')

def draw_subtitle_menu(self, context):
    """Add Subtitles menu to the Sequencer menu bar."""
    self.layout.menu(VSE_MT_subtitle_menu.bl_idname)

# ----------------------- Registration ------------------------

classes = (
    SUBTITLE_OT_import,
    SUBTITLE_OT_export,
    TextInfoSettings,
    TEXT_HT_footer,
    TEXT_Pannel,
    VSEImportSubtitlesOperator,
    VSEExportSubtitlesOperator,
    VSE_MT_subtitle_menu,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TEXT_MT_text.append(menu_func_sub)
    bpy.types.SEQUENCER_MT_editor_menus.append(draw_subtitle_menu)
    bpy.types.Scene.text_info_settings = bpy.props.PointerProperty(type=TextInfoSettings)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.TEXT_MT_text.remove(menu_func_sub)
    bpy.types.SEQUENCER_MT_editor_menus.remove(draw_subtitle_menu)
    del bpy.types.Scene.text_info_settings


if __name__ == "__main__":
    register()
