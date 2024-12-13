# B_SubEditor

B-Sub Editor is a Blender addon designed to streamline subtitle management within the Text Editor and Video Sequence Editor (VSE). It simplifies the process of importing, exporting, and synchronizing subtitles in various formats, including SRT, VTT, SBV, and plain TXT. In the Text Editor, it provides convenient import and export operations, along with a helpful footer displaying text information like line count, cursor position, and selected character count. Within the VSE, B-Sub Editor facilitates the creation of text strips from subtitle files, enabling precise synchronization with video content. This addon aims to enhance the workflow for video editors and content creators who require precise subtitle control within Blender.

![piclumen-1734104081969](https://github.com/user-attachments/assets/f944b27f-7c6d-4e7e-b895-1079dc99b5ee)

**How to Use:**

**Installation:**

1.  Download the addon as a `.zip` file.
2.  In Blender, go to *Edit > Preferences > Add-ons*.
3.  Click *Install...* and select the downloaded `.zip` file.
4.  Enable the addon by checking the box next to "B-Sub Editor" in the Add-ons list.

**Text Editor Usage:**

*   **Importing Subtitles:**
    1.  Open a Text Editor window.
    2.  In the Text Editor header, go to *Text > Import Subtitle*.
    3.  Select the subtitle file you want to import (.srt, .vtt, .sbv, .txt).
    4.  The subtitle content will be imported into a new text block.
*   **Exporting Subtitles:**
    1.  Ensure the Text Editor contains the subtitle content you wish to export.
    2.  In the Text Editor header, go to *Text > Export Subtitle*.
    3.  Choose the desired subtitle format (SRT, VTT, SBV).
    4.  Select a location to save the exported file.
*   **Text Information Footer:**
    *The footer of the Text Editor displays useful information about the current text block, including:*
        *   Total number of lines.
        *   Cursor position (line and column).
        *   Number of selected characters (with an option to include or exclude spaces in the count, controlled by a checkbox in the Text Info panel in the Text Editor's Properties Region).
        * Indentation spaces of the current line.

**VSE Usage:**

*   **Importing Subtitles (from Text Editor):**
    1.  Open a Text Editor and import your subtitle file as described above.
    2.  Open the VSE.
    3.  In the VSE menu bar, go to *Add > Subtitles > Import Subtitles*.
    4.  In the pop-up dialog:
        *   Select the text block containing the subtitles.
        *   Choose the target VSE channel for the text strips.
        *   Check the "Connect Strips" box to automatically connect the created strips end-to-end.
    5. Click OK. Text strips representing the subtitles will be added to the VSE.
*   **Exporting Subtitles (from VSE):**
    1.  In the VSE, select the text strips you want to export.
    2.  In the VSE menu bar, go to *Add > Subtitles > Export Subtitles*.
    3.  The selected subtitles will be exported to a new text block in the Text Editor in SRT format.

**Release Notes:**

**Example Release Notes (v1.0.0):**

*   **New Features:**
    *   Initial release of B-Sub Editor.
    *   Import and export subtitles in SRT, VTT, SBV, and TXT formats within the Text Editor.
    *   Text information footer in the Text Editor with line count, cursor position, selected character count (with space count toggle), and indentation spaces.
    *   Import subtitles from the Text Editor to the VSE as text strips.
    *   Export selected text strips from the VSE to the Text Editor as SRT format.
    *   Basic style support (bold, italic, underline, font size, color) for both import and export.
    *   Option to connect imported strips in VSE.
    *   Improved SBV export with more accurate timecode handling.
    *   Added metadata export to SRT files (title, author, etc.).


*   **Known Issues:**
    *   Complex styling might not be fully supported.
    *   SBV/VTT Imxport/Export is basic.

*   **Community contributions:** Give credit to anyone who helped with the release.

