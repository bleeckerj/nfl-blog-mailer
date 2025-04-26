import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import json
import os
import re
import webbrowser
from pathlib import Path
import tempfile
import jinja2

class TemplateGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NFL Blog Mailer Template Generator")
        # Make window larger to accommodate preview
        self.root.geometry("1200x800")
        
        # Find template directory relative to script location
        script_dir = Path(__file__).parent
        self.templates_dir = script_dir / "templates"
        
        # Dictionary to store template schemas (fields for each template)
        self.template_schemas = self.extract_template_schemas()
        
        # Initialize Jinja2 environment for preview rendering
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(self.templates_dir)))
        
        # Create the main paned window to allow resizing
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for form
        self.left_panel = ttk.Frame(self.paned_window, padding="10")
        self.paned_window.add(self.left_panel, weight=1)
        
        # Right panel for preview
        self.right_panel = ttk.LabelFrame(self.paned_window, text="Live Preview")
        self.paned_window.add(self.right_panel, weight=1)
        
        # Create the main frame for form
        self.main_frame = ttk.Frame(self.left_panel)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create preview area
        self.create_preview_area()
        
        # Create template selection section
        self.create_template_selector()
        
        # Create form area (will be populated when template is selected)
        self.form_frame = ttk.LabelFrame(self.main_frame, text="Template Properties", padding="10")
        self.form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create output area
        self.create_output_area()
        
        # Dictionary to store form fields for accessing later
        self.form_fields = {}
        
        # Setup auto-refresh timer for preview
        self.auto_refresh_preview()

    def extract_template_schemas(self):
        """Extract expected variables from each template file"""
        schemas = {}
        
        # Pattern to match Jinja2 variables: {{ item['variable_name'] }}
        pattern = re.compile(r"{{\s*item\['([^']+)'\]\s*}}")
        
        try:
            for template_file in self.templates_dir.glob("*.html"):
                template_name = template_file.name
                with open(template_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Find all variables in the template
                variables = set(pattern.findall(content))
                
                # Store the schema
                schemas[template_name] = sorted(list(variables))
                
        except Exception as e:
            print(f"Error extracting schemas: {e}")
            
        return schemas

    def create_template_selector(self):
        """Create the template selection dropdown"""
        select_frame = ttk.Frame(self.main_frame)
        select_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(select_frame, text="Select Template:").pack(side=tk.LEFT, padx=5)
        
        # Get sorted list of template files
        template_names = sorted([t for t in self.template_schemas.keys()])
        
        # Create the combobox
        self.template_var = tk.StringVar()
        self.template_selector = ttk.Combobox(
            select_frame, 
            textvariable=self.template_var,
            values=template_names,
            width=40)
        self.template_selector.pack(side=tk.LEFT, padx=5)
        
        # Bind selection event
        self.template_selector.bind("<<ComboboxSelected>>", self.on_template_selected)
        
        # Section name field
        ttk.Label(select_frame, text="Section Name:").pack(side=tk.LEFT, padx=5)
        self.section_name_var = tk.StringVar()
        self.section_name_entry = ttk.Entry(select_frame, textvariable=self.section_name_var, width=20)
        self.section_name_entry.pack(side=tk.LEFT, padx=5)
        
        # Ordinal field
        ttk.Label(select_frame, text="Ordinal:").pack(side=tk.LEFT, padx=5)
        self.ordinal_var = tk.StringVar()
        self.ordinal_entry = ttk.Entry(select_frame, textvariable=self.ordinal_var, width=5)
        self.ordinal_entry.pack(side=tk.LEFT, padx=5)

    def on_template_selected(self, event):
        """Handle template selection"""
        selected_template = self.template_var.get()
        if selected_template:
            self.clear_form()
            self.create_form_for_template(selected_template)
            
            # Set a default section name based on template name if empty
            if not self.section_name_var.get():
                default_name = selected_template.replace('.html', '')
                self.section_name_var.set(default_name)

    def clear_form(self):
        """Clear the form area"""
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        self.form_fields = {}

    def create_form_for_template(self, template_name):
        """Create form fields based on the selected template"""
        if template_name not in self.template_schemas:
            return
            
        variables = self.template_schemas[template_name]
        
        # Create a canvas with scrollbar for the form
        canvas = tk.Canvas(self.form_frame)
        scrollbar = ttk.Scrollbar(self.form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add fields for each variable
        for i, var_name in enumerate(variables):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=5)
            
            # Label
            label = ttk.Label(frame, text=f"{var_name}:", width=20, anchor="e")
            label.pack(side=tk.LEFT, padx=5)
            
            # For certain known fields, create specialized input widgets
            if var_name in ['background_color', 'text_color', 'light_text_color', 'border_color']:
                # Color picker button
                color_var = tk.StringVar(value="#FFFFFF")
                color_entry = ttk.Entry(frame, textvariable=color_var, width=10)
                color_entry.pack(side=tk.LEFT, padx=5)
                
                def pick_color(color_var=color_var):
                    from tkinter import colorchooser
                    color = colorchooser.askcolor()[1]
                    if color:
                        color_var.set(color)
                
                color_btn = ttk.Button(frame, text="Choose...", command=pick_color)
                color_btn.pack(side=tk.LEFT, padx=5)
                
                # Add color swatch display
                swatch_label = ttk.Label(frame, width=3, background=color_var.get())
                swatch_label.pack(side=tk.LEFT, padx=5)
                
                # Update swatch when color changes
                def update_swatch(*args):
                    try:
                        swatch_label.configure(background=color_var.get())
                    except:
                        pass
                color_var.trace_add("write", update_swatch)
                
                self.form_fields[var_name] = color_var
                
            elif var_name == 'image_url':
                # URL input with file browser
                url_var = tk.StringVar()
                url_entry = ttk.Entry(frame, textvariable=url_var, width=40)
                url_entry.pack(side=tk.LEFT, padx=5)
                
                def browse_image():
                    filename = filedialog.askopenfilename(
                        title="Select Image",
                        filetypes=(("Image files", "*.jpg *.jpeg *.png *.gif *.webp"), ("All files", "*.*"))
                    )
                    if filename:
                        url_var.set(filename)
                
                browse_btn = ttk.Button(frame, text="Browse...", command=browse_image)
                browse_btn.pack(side=tk.LEFT, padx=5)
                
                self.form_fields[var_name] = url_var
                
            elif var_name == 'main_copy' or var_name == 'salutation' or var_name.endswith('_text'):
                # Multiline text area
                text_frame = ttk.Frame(scrollable_frame)
                text_frame.pack(fill=tk.X, pady=5)
                
                ttk.Label(text_frame, text=f"{var_name}:", anchor="w").pack(fill=tk.X, padx=5)
                
                text_var = scrolledtext.ScrolledText(text_frame, height=5, width=60)
                text_var.pack(fill=tk.X, padx=5, pady=5)
                
                self.form_fields[var_name] = text_var
                
            elif var_name in ['border_width', 'radius', 'img_border_radius']:
                # Numeric input with units
                frame2 = ttk.Frame(frame)
                frame2.pack(side=tk.LEFT)
                
                num_var = tk.StringVar(value="0")
                num_entry = ttk.Entry(frame2, textvariable=num_var, width=5)
                num_entry.pack(side=tk.LEFT, padx=2)
                
                unit_var = tk.StringVar(value="px")
                unit_combo = ttk.Combobox(frame2, textvariable=unit_var, values=["px", "rem", "%"], width=5)
                unit_combo.pack(side=tk.LEFT, padx=2)
                
                # We need to combine these values when generating JSON
                self.form_fields[var_name] = (num_var, unit_var)
                
            else:
                # Default text input
                var = tk.StringVar()
                entry = ttk.Entry(frame, textvariable=var, width=50)
                entry.pack(side=tk.LEFT, padx=5)
                
                self.form_fields[var_name] = var
        
        # Add generate button
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(pady=15)
        
        generate_button = ttk.Button(buttons_frame, text="Generate JSON", command=self.generate_json)
        generate_button.pack(side=tk.LEFT, padx=5)
        
        preview_button = ttk.Button(buttons_frame, text="Update Preview", command=self.update_preview)
        preview_button.pack(side=tk.LEFT, padx=5)

    def create_output_area(self):
        """Create the output text area"""
        output_frame = ttk.LabelFrame(self.main_frame, text="Generated JSON", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create actions bar
        actions_frame = ttk.Frame(output_frame)
        actions_frame.pack(fill=tk.X, pady=5)
        
        # Add buttons
        copy_btn = ttk.Button(actions_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(actions_frame, text="Save to File", command=self.save_to_file)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        append_btn = ttk.Button(actions_frame, text="Append to JSON", command=self.append_to_json)
        append_btn.pack(side=tk.LEFT, padx=5)
        
        # Create text area for output
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def create_preview_area(self):
        """Create the HTML preview area"""
        # Use a simple HTML viewer approach
        preview_frame = ttk.Frame(self.right_panel, padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_html = scrolledtext.ScrolledText(preview_frame, width=60, height=30)
        self.preview_html.pack(fill=tk.BOTH, expand=True)
        
        # Add a button to open in browser for better rendering
        open_browser_btn = ttk.Button(
            preview_frame, 
            text="Open Preview in Browser", 
            command=self.open_preview_in_browser
        )
        open_browser_btn.pack(pady=10)

    def get_field_value(self, field_key):
        """Extract value from a form field"""
        field = self.form_fields.get(field_key)
        
        if field is None:
            return ""
            
        # Handle different field types
        if isinstance(field, tuple):  # For combined fields like border width
            num_var, unit_var = field
            return f"{num_var.get()}{unit_var.get()}"
            
        elif isinstance(field, scrolledtext.ScrolledText):  # For multiline text
            return field.get("1.0", tk.END).strip()
            
        elif hasattr(field, 'get'):  # For regular variables
            return field.get()
            
        return ""

    def generate_json(self):
        """Generate JSON from form inputs"""
        template_name = self.template_var.get()
        section_name = self.section_name_var.get() or "section_name"
        ordinal = self.ordinal_var.get() or ""
        
        if not template_name:
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, "Please select a template first")
            return
            
        # Create the JSON structure
        json_data = {
            section_name: {
                "metadata": {
                    "template_name": template_name,
                    "ordinal": ordinal
                },
                "elements": [
                    {field: self.get_field_value(field) for field in self.template_schemas[template_name]}
                ]
            }
        }
        
        # Format the JSON with indentation
        formatted_json = json.dumps(json_data, indent=4)
        
        # Update the output area
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, formatted_json)
        
        # Also update the preview
        self.update_preview()

    def update_preview(self):
        """Update the HTML preview"""
        template_name = self.template_var.get()
        
        if not template_name:
            return
            
        try:
            # Get the template
            template = self.jinja_env.get_template(template_name)
            
            # Get the values from form
            item_data = {field: self.get_field_value(field) 
                         for field in self.template_schemas[template_name]}
            
            # Render the template
            rendered_html = template.render(item=item_data)
            
            # Update preview text area
            self.preview_html.delete("1.0", tk.END)
            
            # Add some basic HTML structure for better preview
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Template Preview</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; }}
                    
                    /* Load web fonts for preview */
                    @font-face {{
                        font-family: 'FormaDJRVariable';
                        src: url('https://nearfuturelaboratory.com/fonts/formadjr/FormaDJRVariable[opsz,slnt,wdth,wght].woff2') format('woff2');
                        font-style: normal;
                    }}
                    
                    @font-face {{
                        font-family: 'WarblerText';
                        src: url('https://nearfuturelaboratory.com/fonts/warbler/WarblerTextV1.2-Regular.woff2') format('woff2');
                        font-style: normal;
                        font-weight: 400;
                    }}
                </style>
            </head>
            <body>
                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            {rendered_html}
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
            
            self.preview_html.insert(tk.END, full_html)
            
        except Exception as e:
            self.preview_html.delete("1.0", tk.END)
            self.preview_html.insert(tk.END, f"Error rendering preview: {str(e)}")

    def open_preview_in_browser(self):
        """Open the current preview in a web browser"""
        # Get the HTML
        html_content = self.preview_html.get("1.0", tk.END)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            f.write(html_content.encode('utf-8'))
            temp_path = f.name
            
        # Open in browser
        webbrowser.open(f'file://{temp_path}')

    def auto_refresh_preview(self):
        """Auto-refresh the preview periodically"""
        self.update_preview()
        # Schedule next update in 2 seconds
        self.root.after(2000, self.auto_refresh_preview)

    def copy_to_clipboard(self):
        """Copy the generated JSON to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get("1.0", tk.END))
        
    def save_to_file(self):
        """Save the generated JSON to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.output_text.get("1.0", tk.END))
                
    def append_to_json(self):
        """Append the generated JSON to an existing JSON file"""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Read existing JSON
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                
            # Parse current JSON
            current_json = self.output_text.get("1.0", tk.END)
            current_data = json.loads(current_json)
            
            # Get the section name from the current data
            if not current_data:
                tk.messagebox.showerror("Error", "No JSON data to append")
                return
                
            # Find the section name (first key in the current_data)
            section_name = next(iter(current_data))
            
            # Add the new section to the existing data
            if section_name in existing_data:
                # If section exists, ask user what to do
                action = tk.messagebox.askyesnocancel(
                    "Section exists", 
                    f"The section '{section_name}' already exists in the file.\n\n"
                    "Yes: Replace the existing section\n"
                    "No: Append as a new element to the existing section\n"
                    "Cancel: Abort operation"
                )
                
                if action is None:  # User clicked Cancel
                    return
                    
                if action:  # User clicked Yes - replace section
                    existing_data[section_name] = current_data[section_name]
                else:  # User clicked No - append to elements
                    # Get the new element
                    new_element = current_data[section_name]["elements"][0]
                    # Append it to existing elements
                    existing_data[section_name]["elements"].append(new_element)
            else:
                # Simply add the new section
                existing_data[section_name] = current_data[section_name]
            
            # Write back to file with proper formatting
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=4)
                
            tk.messagebox.showinfo("Success", f"JSON appended to {file_path}")
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to append JSON: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TemplateGeneratorApp(root)
    root.mainloop()