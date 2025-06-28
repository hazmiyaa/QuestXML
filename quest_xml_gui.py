import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import sys

class QuestXMLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Quest XML Generator by Hazmi")
        self.root.geometry("1000x750")
        self.root.minsize(1000, 725)
        
        # Compact color scheme
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db', 
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#34495e',
            'white': '#ffffff',
            'background': '#f8f9fa',
            'card': '#ffffff',
            'border': '#dee2e6',
            'text': '#2c3e50',
            'muted': '#6c757d'
        }
        
        self.root.configure(bg=self.colors['background'])
        
        # Configure compact styling
        self.setup_styles()
        
        # Initialize data structures
        self.quest_data = {}
        self.conditions_data = []
        self.goals_data = []
        self.rewards_data = []
        
        # Better popup management
        self.active_popups = set()
        
        # Define all form fields matching the XML structure
        self.basic_fields = [
            ("UniqID", "2886"), ("Model", "0"), ("Model2", "0"), ("Level", "30"),
            ("Pos", "5"), ("Pos2", "0"), ("ManagedID", "0"), ("Active", "1"),
            ("Unknown", "0"), ("Immediate", "0"), ("ResetQuest", "0"), ("Type", "1"),
            ("StartTargetType", "0"), ("StartTargetID", "93610"), ("Target", "1"), ("TargetValue", "93613")
        ]
        
        self.text_fields = [
            ("TitleTab", "Silver Lake"), ("TitleText", "View from the Top"),
            ("Body", "You haven't been explore to the whole area yet, have you? If you go farther to the right, you will see a high ground.\n\nTalk to the Terriermon there, and he'll show you how to get to the top where you will be able to look down at the whole region."),
            ("Simple", ""), ("Helper", "Speak with Terriermon"), ("Process", "Go on, then. Fly away like me!"),
            ("Complete", "There's nothing like the view from the top! If you have to get to a higher ground, you have come to the right Digimon!"),
            ("Expert", "")
        ]
        
        try:
            self.create_widgets()
            self.create_compact_sidebar()
            self.update_preview()
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize application:\n{str(e)}")
            sys.exit(1)

    def on_closing(self):
        """Proper cleanup when closing application"""
        try:
            for popup in list(self.active_popups):
                try:
                    popup.destroy()
                except tk.TclError:
                    pass
            self.active_popups.clear()
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Error during cleanup: {e}")
            sys.exit(0)

    def setup_styles(self):
        """Configure compact ttk styles"""
        try:
            style = ttk.Style()
            style.theme_use('clam')
            
            # Compact treeview styling
            style.configure("Compact.Treeview", 
                           font=("Segoe UI", 8),
                           rowheight=24,
                           background=self.colors['white'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['white'],
                           borderwidth=1,
                           relief="solid")
            style.configure("Compact.Treeview.Heading", 
                           font=("Segoe UI", 9, "bold"),
                           background=self.colors['secondary'],
                           foreground=self.colors['white'],
                           relief="flat",
                           borderwidth=1)
            
            # Compact notebook styling
            style.configure("Compact.TNotebook", 
                           background=self.colors['background'],
                           borderwidth=0,
                           tabmargins=[1, 2, 1, 0])
            style.configure("Compact.TNotebook.Tab", 
                            padding=[12, 6],
                            font=("Segoe UI", 9, "bold"),
                            background=self.colors['light'],
                            foreground=self.colors['text'],
                            focuscolor=self.colors['light'],  # Hindari perbedaan warna fokus
                            borderwidth=1,
                            relief="solid")
            
            style.map("Compact.TNotebook.Tab",
                            background=[
                                ("selected", self.colors['secondary']),
                                ("active", "#5dade2")
                            ],
                            foreground=[
                                ("selected", self.colors['white']),
                                ("active", self.colors['white'])
                            ],
                            borderwidth=[
                                ("selected", 1),
                                ("active", 1)
                            ],
                            padding=[
                                ("selected", [12, 6]),  # 👈 Samakan padding untuk jaga ukuran
                                ("active", [12, 6])
                            ])
                     
        except Exception as e:
            print(f"Warning: Could not apply custom styles: {e}")

    def create_widgets(self):
        """Create compact main layout"""
        try:
            # Create main container with minimal padding
            main_container = tk.Frame(self.root, bg=self.colors['background'])
            main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
            
            # Create compact header
            self.create_compact_header(main_container)
            
            # Create main content area with sidebar
            content_frame = tk.Frame(main_container, bg=self.colors['background'])
            content_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
            
            # Left side - Main content (75%)
            self.main_content = tk.Frame(content_frame, bg=self.colors['background'])
            self.main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
            
            # Right side - Compact sidebar (25%)
            self.sidebar = tk.Frame(content_frame, bg=self.colors['card'], width=280, relief="flat", bd=0)
            self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
            self.sidebar.pack_propagate(False)
            
            # Create notebook for main content
            self.notebook = ttk.Notebook(self.main_content, style="Compact.TNotebook")
            self.notebook.pack(fill=tk.BOTH, expand=True)
            
            # Create tabs
            self.create_compact_tabs()
            
            # Create compact action buttons at bottom
            self.create_compact_action_buttons(main_container)
            
        except Exception as e:
            raise Exception(f"Failed to create widgets: {str(e)}")

    def create_compact_header(self, parent):
        """Create compact header section"""
        header_frame = tk.Frame(parent, bg=self.colors['primary'], height=50, relief="flat")
        header_frame.pack(fill=tk.X, pady=(0, 8))
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg=self.colors['primary'])
        header_content.pack(expand=True, fill=tk.BOTH, padx=15, pady=10)
        
        # Compact title
        title_label = tk.Label(header_content, 
                              text="🎮 Quest XML Generator", 
                              font=("Segoe UI", 16, "bold"),
                              bg=self.colors['primary'], 
                              fg=self.colors['white'])
        title_label.pack(anchor='w')

    def create_compact_tabs(self):
        """Create compact tabs"""
        # Tab 1: Quest Information
        quest_tab = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(quest_tab, text="📝 Quest")
        
        # Tab 2: Conditions & Goals
        data_tab = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(data_tab, text="🎯 Conditions & Goals")
        
        # Tab 3: Rewards
        reward_tab = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(reward_tab, text="🎁 Rewards")
        
        # Tab 4: XML Preview
        preview_tab = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(preview_tab, text="📄 Preview")
        
        self.create_compact_quest_info_tab(quest_tab)
        self.create_compact_data_tab(data_tab)
        self.create_compact_reward_tab(reward_tab)
        self.create_compact_preview_tab(preview_tab)
        
        self.update_tab_counts()

    def create_compact_sidebar(self):
        """Create compact sidebar without customization section"""
        # Sidebar header
        sidebar_header = tk.Frame(self.sidebar, bg=self.colors['background'], height=50)
        sidebar_header.pack(fill=tk.X)
        sidebar_header.pack_propagate(False)
        
        sidebar_title = tk.Label(sidebar_header, 
                                text="⚙️ Quick Panel", 
                                font=("Segoe UI", 15, "bold"),
                                bg=self.colors['background'], 
                                fg=self.colors['primary'])
        sidebar_title.pack(expand=True)
        
        # Create scrollable content without visible scrollbar
        self.create_hidden_scroll_frame()
        # Additional Settings Section
        self.create_compact_settings_section()
        # Statistics Section
        self.create_compact_statistics_section()
        # Quick Actions Section
        self.create_compact_actions_section()
        


    def create_hidden_scroll_frame(self):
        """Create scrollable frame with hidden scrollbar"""
        # Canvas and internal frame
        self.sidebar_canvas = tk.Canvas(self.sidebar, bg=self.colors['card'], highlightthickness=0)
        self.sidebar_content = tk.Frame(self.sidebar_canvas, bg=self.colors['card'])
        
        # Create window for scrollable content
        self.sidebar_canvas.create_window((0, 0), window=self.sidebar_content, anchor="nw")

        # Update scrollregion
        def update_scrollregion(event=None):
            self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))

        self.sidebar_content.bind("<Configure>", update_scrollregion)

        # Handle mouse wheel only if content overflows
        def _on_sidebar_mousewheel(event):
            try:
                canvas_height = self.sidebar_canvas.winfo_height()
                content_height = self.sidebar_content.winfo_height()
                if content_height > canvas_height:
                    self.sidebar_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass

        self.bind_mousewheel_recursive(self.sidebar, _on_sidebar_mousewheel)
        
        self.sidebar_canvas.pack(fill="both", expand=True)


    def bind_mousewheel_recursive(self, widget, callback):
        """Recursively bind mousewheel to widget and all children"""
        widget.bind("<MouseWheel>", callback)
        for child in widget.winfo_children():
            self.bind_mousewheel_recursive(child, callback)

    def create_compact_settings_section(self):
        """Create compact settings section (responsive layout)"""
        settings_frame = self.create_compact_card_frame(self.sidebar_content, "⚙️ Settings")
        
        self.auto_labels = {}
        settings_data = [
            ("condition", "Conditions", "📋"),
            ("Goals", "Goals", "🎯"), 
            ("RewardNumber", "Rewards", "🎁")
        ]

        for row_index, (key, label, icon) in enumerate(settings_data):
            setting_row = tk.Frame(settings_frame, bg=self.colors['card'])
            setting_row.grid(row=row_index, column=0, sticky="ew", padx=5, pady=3)
            setting_row.columnconfigure(0, weight=1)
            setting_row.columnconfigure(1, weight=0)

            label_widget = tk.Label(
                setting_row,
                text=f"{icon} {label}:",
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=("Segoe UI", 8, "bold"),
                anchor='w'
            )
            label_widget.grid(row=0, column=0, sticky="w")

            count_label = tk.Label(
                setting_row,
                text="0",
                bg=self.colors['light'],
                fg=self.colors['text'],
                font=("Segoe UI", 8, "bold"),
                padx=8,
                pady=3,
                relief="solid",
                bd=1,
                width=3
            )
            count_label.grid(row=0, column=1, sticky="e", padx=(10, 0))

            self.auto_labels[key] = count_label

        settings_frame.columnconfigure(0, weight=1)


    def create_compact_actions_section(self):
        """Create compact quick actions section with responsive layout"""
        actions_frame = self.create_compact_card_frame(self.sidebar_content, "⚡ Actions")
        
        # Compact action buttons (label, function, bg-color)
        quick_actions = [
            ("🔄 Generate", self.safe_update_preview, self.colors['secondary']),
            ("📋 Sample", self.safe_load_sample_data, self.colors['warning']),
            ("📥 Import", self.safe_import_xml, "#9b59b6"),
            ("📄 Line", self.safe_detect_lines, self.colors['success']),
            ("🗑️ Clear", self.safe_clear_all_data, self.colors['danger']),
        ]

        # Responsive grid layout
        columns = 2
        for index, (text, command, color) in enumerate(quick_actions):
            row = index // columns
            col = index % columns
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg=color,
                fg=self.colors['white'],
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                bd=0,
                padx=10,
                pady=6,
                cursor="hand2",
                width=12,
                activebackground=self.darken_color(color),
                activeforeground=self.colors['white']
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.add_button_hover_effect(btn, color)

        # Configure grid weights to make it responsive
        for col in range(columns):
            actions_frame.columnconfigure(col, weight=1)


    def create_compact_statistics_section(self):
        """Create compact statistics section"""
        stats_frame = self.create_compact_card_frame(self.sidebar_content, "📊 Stats")
        
        # Statistics display
        self.stats_labels = {}
        stats_data = [
            ("total_fields", "Fields", "📝"),
            ("completion", "Complete", "✅"),
            ("xml_lines", "XML Lines", "📄")  # Changed from XML Size
        ]
        
        for key, label, icon in stats_data:
            stat_row = tk.Frame(stats_frame, bg=self.colors['card'])
            stat_row.pack(fill=tk.X, pady=2)
            
            tk.Label(stat_row, text=f"{icon} {label}:", 
                    bg=self.colors['card'], fg=self.colors['text'],
                    font=("Segoe UI", 8, "bold"), 
                    anchor='w').pack(side=tk.LEFT)
            
            stat_label = tk.Label(stat_row, text="0", 
                                 bg=self.colors['card'], fg=self.colors['muted'],
                                 font=("Segoe UI", 8),
                                 anchor='e')
            stat_label.pack(side=tk.RIGHT)
            
            self.stats_labels[key] = stat_label
        
        self.update_statistics()

    def create_compact_card_frame(self, parent, title):
        """Create a compact card-style frame"""
        card_container = tk.Frame(parent, bg=self.colors['background'])
        card_container.pack(fill=tk.X, pady=(0, 8), padx=5)
        
        # Main card frame
        card_frame = tk.Frame(card_container, bg=self.colors['card'], relief="solid", bd=1)
        card_frame.pack(fill=tk.X)
        
        # Compact card header
        header_frame = tk.Frame(card_frame, bg=self.colors['light'], height=25)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text=title,
                              font=("Segoe UI", 9, "bold"),
                              bg=self.colors['light'], fg=self.colors['text'])
        title_label.pack(expand=True)
        
        # Compact card content
        content_frame = tk.Frame(card_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        return content_frame

    def create_compact_quest_info_tab(self, parent):
        """Create compact quest information tab with responsive layout"""
        # Canvas container
        canvas = tk.Canvas(parent, bg=self.colors['background'], highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame yang dapat discroll
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])
        frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="frame")

        # Buat scrollable_frame mengikuti lebar canvas
        def resize_scrollable_frame(event):
            canvas.itemconfig(frame_id, width=event.width)

        canvas.bind("<Configure>", resize_scrollable_frame)

        # Scroll region update saat konten berubah
        def update_scrollregion(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", update_scrollregion)

        # Mousewheel: aktif hanya jika konten overflow
        def _on_quest_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    content_height = scrollable_frame.winfo_height()
                    canvas_height = canvas.winfo_height()
                    if content_height > canvas_height:
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass

        self.bind_mousewheel_recursive(parent, _on_quest_mousewheel)

        # Optional: agar child widgets di dalam ikut lebar penuh
        scrollable_frame.columnconfigure(0, weight=1)

        # Tambahkan section/konten
        self.create_compact_basic_fields_section(scrollable_frame)
        self.create_compact_text_fields_section(scrollable_frame)



    def create_compact_basic_fields_section(self, parent):
        """Create compact basic fields section"""
        basic_frame = tk.LabelFrame(parent, text="📊 Basic Information", 
                                   font=("Segoe UI", 10, "bold"),
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   relief="solid", bd=1, padx=10, pady=8,
                                   labelanchor='n')
        basic_frame.pack(fill=tk.X, pady=(0, 8))

        # Create compact grid container
        basic_container = tk.Frame(basic_frame, bg=self.colors['card'])
        basic_container.pack(fill=tk.X, expand=True)

        # Configure grid weights for 4 columns
        for i in range(4):
            basic_container.grid_columnconfigure(i*2+1, weight=1)

        # Create basic fields in compact grid layout
        for i, (label, default) in enumerate(self.basic_fields):
            row = i // 4
            col = (i % 4) * 2
            
            # Compact label styling
            label_widget = tk.Label(basic_container, text=label, 
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=("Segoe UI", 8, "bold"), 
                                   anchor='w')
            label_widget.grid(row=row, column=col, sticky='ew', pady=4, padx=(0, 5))
            
            # Compact entry styling
            entry = tk.Entry(basic_container, width=12, font=("Segoe UI", 8),
                           bg=self.colors['white'], fg=self.colors['text'], 
                           relief="solid", bd=1,
                           insertbackground=self.colors['secondary'],
                           highlightthickness=1,
                           highlightcolor=self.colors['secondary'])
            entry.insert(0, default)
            entry.grid(row=row, column=col+1, pady=4, padx=(0, 10), sticky='ew', ipady=2)
            
            self.add_entry_hover_effect(entry)
            self.quest_data[label] = entry

    def create_compact_text_fields_section(self, parent):
        """Create compact text fields section"""
        text_frame = tk.LabelFrame(parent, text="📝 Text Information", 
                                  font=("Segoe UI", 10, "bold"),
                                  bg=self.colors['card'], fg=self.colors['text'],
                                  relief="solid", bd=1, padx=10, pady=8,
                                  labelanchor='n')
        text_frame.pack(fill=tk.X, pady=(0, 8))

        text_container = tk.Frame(text_frame, bg=self.colors['card'])
        text_container.pack(fill=tk.BOTH, expand=True)
        text_container.grid_columnconfigure(1, weight=1)

        for i, (label, default) in enumerate(self.text_fields):
            # Compact label
            label_widget = tk.Label(text_container, text=f"• {label}", 
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=("Segoe UI", 8, "bold"), 
                                   anchor='w', width=10)
            label_widget.grid(row=i, column=0, sticky='nw', pady=6, padx=(0, 8))
            
            # Determine height based on field type
            height = 6 if label in ("Body", "Complete") else 1
            
            # Compact text widget
            entry = tk.Text(text_container, width=50, height=height, font=("Segoe UI", 8),
                           wrap=tk.WORD, bg=self.colors['white'], fg=self.colors['text'],
                           relief="solid", bd=1,
                           insertbackground=self.colors['secondary'],
                           highlightthickness=1,
                           highlightcolor=self.colors['secondary'],
                           padx=4, pady=3)
            entry.insert("1.0", default)
            entry.grid(row=i, column=1, pady=6, padx=5, sticky='ew')
            
            self.quest_data[label] = entry

    def create_compact_data_tab(self, parent):
        """Create compact data tab with responsive scroll behavior"""
        # Create scrollable canvas
        canvas = tk.Canvas(parent, bg=self.colors['background'], highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # Responsive on resizing
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("frame", width=e.width))

        # Main scrollable container
        main_container = tk.Frame(canvas, bg=self.colors['background'])
        frame_id = canvas.create_window((0, 0), window=main_container, anchor="nw", tags="frame")

        # Update scrollregion on content change
        def update_scrollregion(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        main_container.bind("<Configure>", update_scrollregion)

        # Scroll only when needed
        def _on_data_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    content_height = main_container.winfo_height()
                    canvas_height = canvas.winfo_height()
                    if content_height > canvas_height:
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass

        self.bind_mousewheel_recursive(parent, _on_data_mousewheel)

        # Responsive child container setup
        main_container.columnconfigure(0, weight=1)

        # --- Quest Conditions Section ---
        cond_frame = tk.LabelFrame(main_container, text="🔍 Quest Conditions",
                                font=("Segoe UI", 10, "bold"),
                                bg=self.colors['card'], fg=self.colors['text'],
                                relief="solid", bd=1, padx=10, pady=8,
                                labelanchor='n')
        cond_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 5))
        cond_frame.columnconfigure(0, weight=1)

        self.create_compact_tree_section(cond_frame, "Conditions", "cond",
                                        self.add_condition_popup, self.edit_condition_popup,
                                        self.delete_condition,
                                        ["ConditionType", "ConditionId", "ConditionCount"])

        # --- Quest Goals Section ---
        goal_frame = tk.LabelFrame(main_container, text="🎯 Quest Goals",
                                font=("Segoe UI", 10, "bold"),
                                bg=self.colors['card'], fg=self.colors['text'],
                                relief="solid", bd=1, padx=10, pady=8,
                                labelanchor='n')
        goal_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(5, 8))
        goal_frame.columnconfigure(0, weight=1)

        self.create_compact_tree_section(goal_frame, "Goals", "goal",
                                        self.add_goal_popup, self.edit_goal_popup,
                                        self.delete_goal,
                                        ["GoalType", "GoalId", "GoalCount", "goalAmount", "CurTypeCount", "SubValue", "SubValue1"])


    def create_compact_reward_tab(self, parent):
        """Create compact rewards tab"""
        main_container = tk.Frame(parent, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Compact info panel
        info_frame = tk.Frame(main_container, bg=self.colors['warning'], relief="solid", bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 8))
        
        info_label = tk.Label(info_frame, 
                             text="💡 Reward Types: 0=Money 💰 | 1=Experience ⭐ | 2=Item 🎒",
                             bg=self.colors['warning'], fg=self.colors['white'], 
                             font=("Segoe UI", 9, "bold"),
                             padx=10, pady=6)
        info_label.pack()
        
        # Compact reward frame
        reward_frame = tk.LabelFrame(main_container, text="🎁 Reward Quantities", 
                                    font=("Segoe UI", 10, "bold"),
                                    bg=self.colors['card'], fg=self.colors['text'],
                                    relief="solid", bd=1, padx=10, pady=8,
                                    labelanchor='n')
        reward_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_compact_tree_section(reward_frame, "Rewards", "reward", 
                                        self.add_reward_popup, self.edit_reward_popup, 
                                        self.delete_reward, ["Reward", "RewardType", "RewardMoney", "RewardItem", "RewardAmount"])

    def create_compact_preview_tab(self, parent):
        """Create compact XML preview tab with line detection"""
        preview_frame = tk.LabelFrame(parent, text="📄 XML Preview",
                                     font=("Segoe UI", 10, "bold"),
                                     bg=self.colors['card'], fg=self.colors['text'],
                                     relief="solid", bd=1, padx=10, pady=8,
                                     labelanchor='n')
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Compact button frame
        button_frame = tk.Frame(preview_frame, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Font size controls
        font_frame = tk.Frame(button_frame, bg=self.colors['card'])
        font_frame.pack(side=tk.LEFT)
        
        tk.Label(font_frame, text="Font:", bg=self.colors['card'], fg=self.colors['text'],
                font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        self.font_size_var = tk.IntVar(value=9)
        font_spin = tk.Spinbox(font_frame, from_=6, to=16, width=3, 
                              textvariable=self.font_size_var,
                              command=self.update_font_size,
                              font=("Segoe UI", 8))
        font_spin.pack(side=tk.LEFT, padx=(0, 10))
        
        # Compact buttons
        copy_btn = tk.Button(button_frame, text="📋 Copy", 
                           command=self.safe_copy_xml_to_clipboard,
                           bg="#17a2b8", fg=self.colors['white'], 
                           font=("Segoe UI", 8, "bold"),
                           relief="flat", bd=0, padx=12, pady=4,
                           cursor="hand2")
        copy_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        save_xml_btn = tk.Button(button_frame, text="💾 Save", 
                               command=self.safe_save_xml,
                               bg=self.colors['success'], fg=self.colors['white'], 
                               font=("Segoe UI", 8, "bold"),
                               relief="flat", bd=0, padx=12, pady=4,
                               cursor="hand2")
        save_xml_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Line info display
        self.line_info_label = tk.Label(button_frame, text="Lines: 0", 
                                       bg=self.colors['card'], fg=self.colors['muted'],
                                       font=("Segoe UI", 8))
        self.line_info_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Enhanced text widget for XML preview with hidden scrollbar
        text_frame = tk.Frame(preview_frame, bg=self.colors['card'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.xml_text = tk.Text(text_frame, wrap=tk.WORD, 
                               font=("Consolas", self.font_size_var.get()),
                               bg="#1e1e1e", fg="#d4d4d4", 
                               insertbackground='#ffffff',
                               selectbackground="#264f78",
                               relief="solid", bd=1,
                               padx=5, pady=5)
        self.xml_text.pack(fill=tk.BOTH, expand=True)
        
        # Hidden scroll for XML text
        def _on_xml_mousewheel(event):
            try:
                if self.xml_text.winfo_exists():
                    self.xml_text.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass
        
        self.xml_text.bind("<MouseWheel>", _on_xml_mousewheel)

    def create_compact_tree_section(self, parent, title, prefix, add_fn, edit_fn, del_fn, headers):
        """Create compact tree section"""
        # Compact treeview container
        tree_container = tk.Frame(parent, bg=self.colors['card'])
        tree_container.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        # Create compact treeview
        columns = [f"col{i}" for i in range(len(headers))]
        tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                           height=6, style="Compact.Treeview")
        
        # Configure headers
        for i, header in enumerate(headers):
            tree.heading(f"col{i}", text=header)
            tree.column(f"col{i}", width=80, anchor='center', minwidth=60)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        setattr(self, f"{prefix}_tree", tree)
        
        # Compact button frame
        btn_frame = tk.Frame(parent, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Compact buttons
        buttons = [
            ("➕ Add", add_fn, self.colors['success']),
            ("✏️ Edit", edit_fn, self.colors['warning']),
            ("🗑️ Delete", del_fn, self.colors['danger'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=self.safe_wrapper(command),
                           bg=color, fg=self.colors['white'], 
                           font=("Segoe UI", 8, "bold"),
                           relief="flat", bd=0, padx=12, pady=4,
                           cursor="hand2")
            btn.pack(side=tk.LEFT, padx=(4, 2))
            self.add_button_hover_effect(btn, color)

    def create_compact_action_buttons(self, parent):
        """Create compact action buttons at bottom"""
        action_frame = tk.Frame(parent, bg=self.colors['primary'], height=40, relief="flat")
        action_frame.pack(fill=tk.X, pady=(8, 0))
        action_frame.pack_propagate(False)
        
        # Button container
        btn_container = tk.Frame(action_frame, bg=self.colors['primary'])
        btn_container.pack(expand=True)
        
        # Compact status label
        self.status_label = tk.Label(btn_container, 
                                    text="Ready to create your quest XML",
                                    bg=self.colors['primary'], fg=self.colors['light'],
                                    font=("Segoe UI", 8))
        self.status_label.pack(side=tk.LEFT, padx=15)
        
        # Compact main action button
        generate_btn = tk.Button(btn_container, text="🚀 Generate XML", 
                               command=self.safe_update_preview,
                               bg=self.colors['success'], fg=self.colors['white'], 
                               font=("Segoe UI", 10, "bold"),
                               relief="flat", bd=0, padx=20, pady=6,
                               cursor="hand2")
        generate_btn.pack(side=tk.RIGHT, padx=15)

    # Helper methods
    def add_entry_hover_effect(self, widget):
        """Add hover effect to entry widgets"""
        def on_enter(e):
            try:
                if widget.winfo_exists():
                    widget.configure(highlightbackground=self.colors['secondary'])
            except tk.TclError:
                pass
        
        def on_leave(e):
            try:
                if widget.winfo_exists():
                    widget.configure(highlightbackground=self.colors['border'])
            except tk.TclError:
                pass
        
        try:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        except Exception as e:
            print(f"Warning: Could not add hover effect: {e}")

    def add_button_hover_effect(self, button, original_color):
        """Add hover effect to buttons"""
        def on_enter(e):
            try:
                if button.winfo_exists():
                    button.configure(bg=self.lighten_color(original_color))
            except tk.TclError:
                pass
        
        def on_leave(e):
            try:
                if button.winfo_exists():
                    button.configure(bg=original_color)
            except tk.TclError:
                pass
        
        try:
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        except Exception as e:
            print(f"Warning: Could not add button hover effect: {e}")

    def darken_color(self, color):
        """Darken a hex color"""
        if color.startswith('#'):
            color = color[1:]
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, c - 30) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def lighten_color(self, color):
        """Lighten a hex color"""
        if color.startswith('#'):
            color = color[1:]
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, c + 20) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def update_font_size(self):
        """Update XML preview font size"""
        try:
            new_size = self.font_size_var.get()
            self.xml_text.configure(font=("Consolas", new_size))
        except Exception as e:
            print(f"Warning: Could not update font size: {e}")

    def update_statistics(self):
        """Update statistics in sidebar"""
        try:
            # Total fields filled
            filled_fields = 0
            total_fields = len(self.basic_fields) + len(self.text_fields)
            
            for field_name, _ in self.basic_fields + self.text_fields:
                if field_name in self.quest_data:
                    widget = self.quest_data[field_name]
                    if isinstance(widget, tk.Text):
                        value = widget.get("1.0", tk.END).strip()
                    else:
                        value = widget.get().strip()
                    if value:
                        filled_fields += 1
            
            self.stats_labels['total_fields'].configure(text=f"{filled_fields}/{total_fields}")
            
            # Completion percentage
            completion = int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
            self.stats_labels['completion'].configure(text=f"{completion}%")
            
            # XML lines count
            xml_content = self.xml_text.get("1.0", tk.END).strip() if hasattr(self, 'xml_text') else ""
            xml_lines = len(xml_content.split('\n')) if xml_content else 0
            self.stats_labels['xml_lines'].configure(text=str(xml_lines))
            
            # Update line info in preview tab
            if hasattr(self, 'line_info_label'):
                self.line_info_label.configure(text=f"Lines: {xml_lines}")
            
        except Exception as e:
            print(f"Warning: Could not update statistics: {e}")

    def update_auto_counts(self):
        """Update the auto-calculated counts display"""
        try:
            if hasattr(self, 'auto_labels'):
                # Update condition count
                cond_count = len(self.conditions_data)
                if 'condition' in self.auto_labels:
                    self.auto_labels['condition'].configure(text=str(cond_count))
                    if cond_count == 0:
                        self.auto_labels['condition'].configure(bg="#f8d7da", fg="#721c24")
                    else:
                        self.auto_labels['condition'].configure(bg="#d4edda", fg="#155724")
                
                # Update goals count
                goal_count = len(self.goals_data)
                if 'Goals' in self.auto_labels:
                    self.auto_labels['Goals'].configure(text=str(goal_count))
                    if goal_count == 0:
                        self.auto_labels['Goals'].configure(bg="#f8d7da", fg="#721c24")
                    else:
                        self.auto_labels['Goals'].configure(bg="#d4edda", fg="#155724")
                
                # Update reward count
                reward_count = len(self.rewards_data)
                if 'RewardNumber' in self.auto_labels:
                    self.auto_labels['RewardNumber'].configure(text=str(reward_count))
                    if reward_count == 0:
                        self.auto_labels['RewardNumber'].configure(bg="#f8d7da", fg="#721c24")
                    elif reward_count <= 3:
                        self.auto_labels['RewardNumber'].configure(bg="#fff3cd", fg="#856404")
                    else:
                        self.auto_labels['RewardNumber'].configure(bg="#d4edda", fg="#155724")
                        
            # Update statistics
            self.update_statistics()
            
        except Exception as e:
            print(f"Warning: Could not update auto counts: {e}")

    def update_tab_counts(self):
        """Update tab labels with counts"""
        try:
            # Update Conditions & Goals tab
            cond_count = len(self.conditions_data)
            goal_count = len(self.goals_data)
            self.notebook.tab(1, text=f"🎯 Conditions & Goals (C:{cond_count} G:{goal_count})")
            
            # Update Rewards tab
            reward_count = len(self.rewards_data)
            self.notebook.tab(2, text=f"🎁 Rewards ({reward_count})")
        except Exception as e:
            print(f"Warning: Could not update tab counts: {e}")

    # Safe wrapper methods
    def safe_wrapper(self, func):
        """Create safe wrapper for functions"""
        def wrapper():
            try:
                func()
            except Exception as e:
                messagebox.showerror("Error", f"Operation failed:\n{str(e)}")
        return wrapper

    def safe_update_preview(self):
        """Safe wrapper for update_preview"""
        try:
            self.update_preview()
            self.status_label.configure(text="XML generated successfully!")
            self.root.after(3000, lambda: self.status_label.configure(text="Ready to create your quest XML"))
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to generate XML preview:\n{str(e)}")
            self.status_label.configure(text="Error generating XML")

    def safe_detect_lines(self):
        """Detect and highlight lines in XML preview"""
        try:
            xml_content = self.xml_text.get("1.0", tk.END).strip()
            if not xml_content:
                messagebox.showwarning("No Content", "Generate XML first to detect lines.")
                return
            
            lines = xml_content.split('\n')
            line_count = len(lines)
            
            # Find important lines (elements with actual data)
            important_lines = []
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith('<?xml') and not line_stripped.startswith('<QuestInfo') and not line_stripped.endswith('</QuestInfo>'):
                    if '>' in line_stripped and '</' in line_stripped:  # Complete element
                        important_lines.append(i)
            
            # Show line detection results
            result_msg = f"📄 XML Line Detection Results:\n\n"
            result_msg += f"Total Lines: {line_count}\n"
            result_msg += f"Data Lines: {len(important_lines)}\n"
            result_msg += f"Empty/Structure Lines: {line_count - len(important_lines)}\n\n"
            result_msg += f"Important line numbers: {', '.join(map(str, important_lines[:10]))}"
            if len(important_lines) > 10:
                result_msg += f"... and {len(important_lines) - 10} more"
            
            messagebox.showinfo("Line Detection", result_msg)
            
            # Update line info
            self.line_info_label.configure(text=f"Lines: {line_count} (Data: {len(important_lines)})")
            
        except Exception as e:
            messagebox.showerror("Line Detection Error", f"Failed to detect lines:\n{str(e)}")

    def safe_clear_all_data(self):
        """Safe wrapper for clear_all_data"""
        try:
            self.clear_all_data()
        except Exception as e:
            messagebox.showerror("Clear Error", f"Failed to clear data:\n{str(e)}")

    def safe_import_xml(self):
        """Safe wrapper for import_xml"""
        try:
            self.import_xml()
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import XML:\n{str(e)}")

    def safe_load_sample_data(self):
        """Safe wrapper for load_sample_data"""
        try:
            self.load_sample_data()
        except Exception as e:
            messagebox.showerror("Sample Data Error", f"Failed to load sample data:\n{str(e)}")

    def safe_copy_xml_to_clipboard(self):
        """Safe wrapper for copy_xml_to_clipboard"""
        try:
            self.copy_xml_to_clipboard()
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy XML:\n{str(e)}")

    def safe_save_xml(self):
        """Safe wrapper for save_xml"""
        try:
            self.save_xml()
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save XML:\n{str(e)}")

    # Core functionality methods (keeping the original logic but compact)
    def get_quest_field_value(self, field_name):
        """Get value from quest field"""
        try:
            if field_name not in self.quest_data:
                return ""
            
            widget = self.quest_data[field_name]
            if isinstance(widget, tk.Text):
                return widget.get("1.0", tk.END).strip()
            else:
                return widget.get().strip()
        except Exception as e:
            print(f"Warning: Could not get value for {field_name}: {e}")
            return ""

    def generate_xml(self):
        """Generate XML with proper structure"""
        try:
            root = ET.Element("QuestInfo")
            
            # Add basic fields in correct order
            basic_field_order = [
                "UniqID", "Model", "Model2", "Level", "Pos", "Pos2", 
                "ManagedID", "Active", "Unknown", "Immediate", "ResetQuest", 
                "Type", "StartTargetType", "StartTargetID", "Target", "TargetValue"
            ]
            
            for field_name in basic_field_order:
                elem = ET.SubElement(root, field_name)
                elem.text = self.get_quest_field_value(field_name)
            
            # Add text fields in correct order
            text_field_order = [
                "TitleTab", "TitleText", "Body", "Simple", 
                "Helper", "Process", "Complete", "Expert"
            ]
            
            for field_name in text_field_order:
                elem = ET.SubElement(root, field_name)
                elem.text = self.get_quest_field_value(field_name)
            
            # Add condition count and conditions
            condition_elem = ET.SubElement(root, "condition")
            condition_elem.text = str(len(self.conditions_data))
            
            if self.conditions_data:
                quest_conditions = ET.SubElement(root, "QuestConditions")
                for condition in self.conditions_data:
                    quest_condition = ET.SubElement(quest_conditions, "QuestCondition")
                    
                    cond_type = ET.SubElement(quest_condition, "ConditionType")
                    cond_type.text = str(condition.get("ConditionType", 0))
                    
                    cond_id = ET.SubElement(quest_condition, "ConditionId")
                    cond_id.text = str(condition.get("ConditionId", 0))
                    
                    cond_count = ET.SubElement(quest_condition, "ConditionCount")
                    cond_count.text = str(condition.get("ConditionCount", 0))
            
            # Add goals count and goals
            goals_elem = ET.SubElement(root, "Goals")
            goals_elem.text = str(len(self.goals_data))
            
            if self.goals_data:
                quest_goals = ET.SubElement(root, "QuestGoals")
                for goal in self.goals_data:
                    quest_goal = ET.SubElement(quest_goals, "QuestGoal")
                    
                    goal_type = ET.SubElement(quest_goal, "GoalType")
                    goal_type.text = str(goal.get("GoalType", 0))
                    
                    goal_id = ET.SubElement(quest_goal, "GoalId")
                    goal_id.text = str(goal.get("GoalId", 0))
                    
                    goal_count = ET.SubElement(quest_goal, "GoalCount")
                    goal_count.text = str(goal.get("GoalCount", 0))
                    
                    goal_amount = ET.SubElement(quest_goal, "goalAmount")
                    goal_amount.text = str(goal.get("goalAmount", 0))
                    
                    cur_type_count = ET.SubElement(quest_goal, "CurTypeCount")
                    cur_type_count.text = str(goal.get("CurTypeCount", 0))
                    
                    sub_value = ET.SubElement(quest_goal, "SubValue")
                    sub_value.text = str(goal.get("SubValue", 0))
                    
                    sub_value1 = ET.SubElement(quest_goal, "SubValue1")
                    sub_value1.text = str(goal.get("SubValue1", 0))
            
            # Add reward number and rewards
            reward_number_elem = ET.SubElement(root, "RewardNumber")
            reward_number_elem.text = str(len(self.rewards_data))
            
            if self.rewards_data:
                reward_quantities = ET.SubElement(root, "RewardQuantities")
            
                for reward in self.rewards_data:
                    reward_quantity = ET.SubElement(reward_quantities, "RewardQuantity")
                
                    reward_elem = ET.SubElement(reward_quantity, "Reward")
                    reward_elem.text = str(reward.get("Reward", 0))
                
                    reward_type = ET.SubElement(reward_quantity, "RewardType")
                    reward_type.text = str(reward.get("RewardType", 0))
                
                    # Handle different reward types
                    if reward.get("RewardType", 0) == 0:  # Money reward
                        quest_reward_money = ET.SubElement(reward_quantity, "QuestRewardMoney")
                        quest_reward_money_item = ET.SubElement(quest_reward_money, "QuestRewardMoneyItem")
                        reward_money = ET.SubElement(quest_reward_money_item, "RewardMoney")
                        reward_money.text = str(reward.get("RewardMoney", 0))
                        reward_unk = ET.SubElement(quest_reward_money_item, "RewardUnk")
                        reward_unk.text = "0"
                    
                        quest_reward_items = ET.SubElement(reward_quantity, "QuestRewardItems")
                    
                    else:  # Item reward
                        quest_reward_money = ET.SubElement(reward_quantity, "QuestRewardMoney")
                    
                        quest_reward_items = ET.SubElement(reward_quantity, "QuestRewardItems")
                        quest_reward_items_item = ET.SubElement(quest_reward_items, "QuestRewardItemsItem")
                        reward_item = ET.SubElement(quest_reward_items_item, "RewardItem")
                        reward_item.text = str(reward.get("RewardItem", 0))
                        reward_amount = ET.SubElement(quest_reward_items_item, "RewardAmount")
                        reward_amount.text = str(reward.get("RewardAmount", 0))
        
            # Add QuestItems and Event sections
            quest_items = ET.SubElement(root, "QuestItems")
        
            event = ET.SubElement(root, "Event")
            for i in range(4):
                event_id = ET.SubElement(event, "EventId")
                event_id.text = "0"
        
            return root
            
        except Exception as e:
            raise Exception(f"Failed to generate XML: {str(e)}")

    def update_preview(self):
        """Update XML preview"""
        try:
            xml_tree = self.generate_xml()
            rough_string = ET.tostring(xml_tree, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
        
            if hasattr(self, 'xml_text'):
                self.xml_text.delete(1.0, tk.END)
                self.xml_text.insert(tk.END, pretty_xml)
                
            # Update counts and statistics
            self.update_auto_counts()
        
        except Exception as e:
            if hasattr(self, 'xml_text'):
                self.xml_text.delete(1.0, tk.END)
                self.xml_text.insert(tk.END, f"Error generating XML: {str(e)}")
            print(f"XML Preview Error: {e}")

    def copy_xml_to_clipboard(self):
        """Copy XML content to clipboard"""
        try:
            xml_content = self.xml_text.get("1.0", tk.END).strip()
            if xml_content:
                self.root.clipboard_clear()
                self.root.clipboard_append(xml_content)
                self.root.update()
                messagebox.showinfo("Copy Success", "✅ XML copied to clipboard successfully!")
            else:
                messagebox.showwarning("No Content", "⚠️ No XML content to copy. Generate XML first.")
        except Exception as e:
            raise Exception(f"Failed to copy XML to clipboard: {str(e)}")

    def save_xml(self):
        """Save XML to file"""
        try:
            quest_id = self.get_quest_field_value("UniqID")
            title = self.get_quest_field_value("TitleTab").replace(" ", "_").replace("/", "_").replace("\\", "_")
            default_filename = f"Quest_{quest_id}_{title}.xml"

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xml",
                initialname=default_filename,
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                title="Save Quest XML File"
            )

            if file_path:
                xml_tree = self.generate_xml()
                rough_string = ET.tostring(xml_tree, 'utf-8')
                reparsed = minidom.parseString(rough_string)
                pretty_xml = reparsed.toprettyxml(indent="  ", encoding=None)

                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    lines = pretty_xml.split('\n')[1:]
                    f.write('\n'.join(lines))

                file_size = os.path.getsize(file_path)
                messagebox.showinfo("Save Berhasil", 
                                  f"✅ XML berhasil disimpan!\n\n"
                                  f"📁 Lokasi: {file_path}\n"
                                  f"📊 Ukuran: {file_size} bytes\n"
                                  f"🆔 Quest ID: {quest_id}",
                                  icon='info')
        except Exception as e:
            raise Exception(f"Failed to save XML file: {str(e)}")

    def clear_all_data(self):
        """Clear all form data and reset to defaults"""
        try:
            if messagebox.askyesno("Confirm Clear", 
                                  "Apakah Anda yakin ingin menghapus semua data?\nTindakan ini tidak dapat dibatalkan.",
                                  icon='warning'):

                # Reset all fields to defaults
                all_fields = self.basic_fields + self.text_fields
                for field_name, default_value in all_fields:
                    if field_name in self.quest_data:
                        widget = self.quest_data[field_name]
                        if isinstance(widget, tk.Text):
                            widget.delete("1.0", tk.END)
                            widget.insert("1.0", default_value)
                        else:
                            widget.delete(0, tk.END)
                            widget.insert(0, default_value)

                # Clear all data lists
                self.conditions_data.clear()
                self.goals_data.clear()
                self.rewards_data.clear()

                # Clear all treeviews
                if hasattr(self, 'cond_tree'):
                    for item in self.cond_tree.get_children():
                        self.cond_tree.delete(item)
                if hasattr(self, 'goal_tree'):
                    for item in self.goal_tree.get_children():
                        self.goal_tree.delete(item)
                if hasattr(self, 'reward_tree'):
                    for item in self.reward_tree.get_children():
                        self.reward_tree.delete(item)

                self.update_auto_counts()
                self.update_tab_counts()
                self.update_preview()
                messagebox.showinfo("Clear Berhasil", "Semua data berhasil dihapus dan direset ke default.")
        except Exception as e:
            raise Exception(f"Failed to clear data: {str(e)}")

    def load_sample_data(self):
        """Load sample quest data"""
        try:
            if messagebox.askyesno("Load Sample Data", 
                                  "Apakah Anda yakin ingin memuat sample data?\nData yang ada akan diganti.",
                                  icon='question'):
                
                # Clear existing data first
                self.conditions_data.clear()
                self.goals_data.clear()
                self.rewards_data.clear()
                
                # Load sample data
                sample_conditions = [
                    {"ConditionType": 1, "ConditionId": 30, "ConditionCount": 0},
                    {"ConditionType": 3, "ConditionId": 44, "ConditionCount": 0}
                ]
                
                sample_goals = [
                    {
                        "GoalType": 4,
                        "GoalId": 93609,
                        "GoalCount": 0,
                        "goalAmount": 1,
                        "CurTypeCount": 0,
                        "SubValue": 0,
                        "SubValue1": 0
                    }
                ]
                
                sample_rewards = [
                    {"Reward": 0, "RewardType": 0, "RewardMoney": 800, "RewardItem": 0, "RewardAmount": 0},
                    {"Reward": 0, "RewardType": 1, "RewardMoney": 0, "RewardItem": 400000, "RewardAmount": 0}
                ]
                
                # Add sample data
                self.conditions_data.extend(sample_conditions)
                self.goals_data.extend(sample_goals)
                self.rewards_data.extend(sample_rewards)
                
                # Update displays
                self.refresh_all_treeviews()
                self.update_auto_counts()
                self.update_tab_counts()
                self.update_preview()
                
                messagebox.showinfo("Sample Data Loaded", 
                                  f"✅ Sample data berhasil dimuat!\n\n"
                                  f"📊 Conditions: {len(self.conditions_data)}\n"
                                  f"🎯 Goals: {len(self.goals_data)}\n"
                                  f"🎁 Rewards: {len(self.rewards_data)}")
        except Exception as e:
            raise Exception(f"Failed to load sample data: {str(e)}")

    def refresh_all_treeviews(self):
        """Refresh all treeview displays"""
        try:
            # Clear all treeviews
            if hasattr(self, 'cond_tree'):
                for item in self.cond_tree.get_children():
                    self.cond_tree.delete(item)
            if hasattr(self, 'goal_tree'):
                for item in self.goal_tree.get_children():
                    self.goal_tree.delete(item)
            if hasattr(self, 'reward_tree'):
                for item in self.reward_tree.get_children():
                    self.reward_tree.delete(item)
            
            # Repopulate treeviews
            if hasattr(self, 'cond_tree'):
                for condition in self.conditions_data:
                    self.cond_tree.insert("", tk.END, values=tuple(condition.values()))
            
            if hasattr(self, 'goal_tree'):
                for goal in self.goals_data:
                    self.goal_tree.insert("", tk.END, values=tuple(goal.values()))
            
            if hasattr(self, 'reward_tree'):
                for reward in self.rewards_data:
                    self.reward_tree.insert("", tk.END, values=tuple(reward.values()))
        except Exception as e:
            print(f"Warning: Could not refresh treeviews: {e}")

    def import_xml(self):
        """Import XML file and populate form"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                title="Import Quest XML File"
            )
            
            if not file_path:
                return
            
            if not os.path.exists(file_path):
                messagebox.showerror("File Error", "Selected file does not exist.")
                return
            
            # Parse XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            if messagebox.askyesno("Import XML", 
                                  "Apakah Anda yakin ingin mengimport XML?\nData yang ada akan diganti.",
                                  icon='question'):
                
                # Clear existing data
                self.conditions_data.clear()
                self.goals_data.clear()
                self.rewards_data.clear()
                
                # Import basic fields
                for field_name, _ in self.basic_fields:
                    elem = root.find(field_name)
                    if elem is not None and elem.text and field_name in self.quest_data:
                        widget = self.quest_data[field_name]
                        if isinstance(widget, tk.Text):
                            widget.delete("1.0", tk.END)
                            widget.insert("1.0", elem.text)
                        else:
                            widget.delete(0, tk.END)
                            widget.insert(0, elem.text)
                
                # Import text fields
                for field_name, _ in self.text_fields:
                    elem = root.find(field_name)
                    if elem is not None and elem.text and field_name in self.quest_data:
                        widget = self.quest_data[field_name]
                        widget.delete("1.0", tk.END)
                        widget.insert("1.0", elem.text)
                
                # Import conditions
                quest_conditions = root.find("QuestConditions")
                if quest_conditions is not None:
                    for quest_condition in quest_conditions.findall("QuestCondition"):
                        condition_data = {}
                        for field in ["ConditionType", "ConditionId", "ConditionCount"]:
                            elem = quest_condition.find(field)
                            condition_data[field] = int(elem.text) if elem is not None and elem.text else 0
                        self.conditions_data.append(condition_data)
                
                # Import goals
                quest_goals = root.find("QuestGoals")
                if quest_goals is not None:
                    for quest_goal in quest_goals.findall("QuestGoal"):
                        goal_data = {}
                        for field in ["GoalType", "GoalId", "GoalCount", "goalAmount", "CurTypeCount", "SubValue", "SubValue1"]:
                            elem = quest_goal.find(field)
                            goal_data[field] = int(elem.text) if elem is not None and elem.text else 0
                        self.goals_data.append(goal_data)
                
                # Import rewards
                reward_quantities = root.find("RewardQuantities")
                if reward_quantities is not None:
                    for reward_quantity in reward_quantities.findall("RewardQuantity"):
                        reward_data = {"Reward": 0, "RewardType": 0, "RewardMoney": 0, "RewardItem": 0, "RewardAmount": 0}
                        
                        # Get basic reward info
                        reward_elem = reward_quantity.find("Reward")
                        if reward_elem is not None and reward_elem.text:
                            reward_data["Reward"] = int(reward_elem.text)
                        
                        reward_type_elem = reward_quantity.find("RewardType")
                        if reward_type_elem is not None and reward_type_elem.text:
                            reward_data["RewardType"] = int(reward_type_elem.text)
                        
                        # Get money reward
                        quest_reward_money = reward_quantity.find("QuestRewardMoney")
                        if quest_reward_money is not None:
                            money_item = quest_reward_money.find("QuestRewardMoneyItem")
                            if money_item is not None:
                                money_elem = money_item.find("RewardMoney")
                                if money_elem is not None and money_elem.text:
                                    reward_data["RewardMoney"] = int(money_elem.text)
                        
                        # Get item reward
                        quest_reward_items = reward_quantity.find("QuestRewardItems")
                        if quest_reward_items is not None:
                            items_item = quest_reward_items.find("QuestRewardItemsItem")
                            if items_item is not None:
                                item_elem = items_item.find("RewardItem")
                                amount_elem = items_item.find("RewardAmount")
                                if item_elem is not None and item_elem.text:
                                    reward_data["RewardItem"] = int(item_elem.text)
                                if amount_elem is not None and amount_elem.text:
                                    reward_data["RewardAmount"] = int(amount_elem.text)
                        
                        self.rewards_data.append(reward_data)
                
                # Refresh displays
                self.refresh_all_treeviews()
                self.update_auto_counts()
                self.update_tab_counts()
                self.update_preview()
                
                messagebox.showinfo("Import Berhasil", 
                                  f"✅ XML berhasil diimport!\n\n"
                                  f"📁 File: {os.path.basename(file_path)}\n"
                                  f"📊 Conditions: {len(self.conditions_data)}\n"
                                  f"🎯 Goals: {len(self.goals_data)}\n"
                                  f"🎁 Rewards: {len(self.rewards_data)}")
        
        except ET.ParseError as e:
            messagebox.showerror("XML Parse Error", f"❌ Invalid XML file:\n{str(e)}")
        except Exception as e:
            raise Exception(f"Failed to import XML: {str(e)}")

    # Popup methods for adding/editing data
    def open_popup(self, title, fields, callback, values=None):
        """Create compact popup dialog"""
        try:
            popup = tk.Toplevel(self.root)
            popup.title(title)
            popup.geometry("350x400")
            popup.resizable(False, False)
            popup.configure(bg=self.colors['card'])
            popup.transient(self.root)
            popup.grab_set()
            
            # Track this popup
            self.active_popups.add(popup)
            
            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (350 // 2)
            y = (popup.winfo_screenheight() // 2) - (400 // 2)
            popup.geometry(f"350x400+{x}+{y}")
            
            # Cleanup function
            def cleanup_popup():
                try:
                    if popup in self.active_popups:
                        self.active_popups.remove(popup)
                    popup.destroy()
                except tk.TclError:
                    pass

            popup.protocol("WM_DELETE_WINDOW", cleanup_popup)
            
            # Create popup content
            self.create_compact_popup_content(popup, title, fields, callback, values, cleanup_popup)
            
        except Exception as e:
            messagebox.showerror("Popup Error", f"Failed to create popup:\n{str(e)}")

    def create_compact_popup_content(self, popup, title, fields, callback, values, cleanup_func):
        """Create compact popup content"""
        try:
            # Compact header
            header_frame = tk.Frame(popup, bg=self.colors['secondary'], height=40)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
        
            title_label = tk.Label(header_frame, text=title, 
                              font=("Segoe UI", 11, "bold"),
                              bg=self.colors['secondary'], fg=self.colors['white'])
            title_label.pack(expand=True)
        
            # Button frame at bottom
            btn_frame = tk.Frame(popup, bg=self.colors['card'], height=50)
            btn_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=8)
            btn_frame.pack_propagate(False)
        
            btn_container = tk.Frame(btn_frame, bg=self.colors['card'])
            btn_container.pack(expand=True)
        
            # Main content with hidden scrolling
            canvas = tk.Canvas(popup, bg=self.colors['card'], highlightthickness=0)
            main_frame = tk.Frame(canvas, bg=self.colors['card'])
        
            main_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
            # Hidden scroll functionality
            def _on_popup_mousewheel(event):
                try:
                    if canvas.winfo_exists():
                        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                except tk.TclError:
                    pass
        
            canvas.bind("<MouseWheel>", _on_popup_mousewheel)
        
            # Create compact form fields
            entries = {}
            for i, field in enumerate(fields):
                field_frame = tk.Frame(main_frame, bg=self.colors['card'])
                field_frame.pack(fill=tk.X, pady=4, padx=15)
            
                # Field descriptions for rewards
                field_descriptions = {
                    "Reward": "Reward index (usually 0)",
                    "RewardType": "0=Money 💰, 1=Experience ⭐, 2=Item 🎒",
                    "RewardMoney": "Amount of money (if RewardType=0)",
                    "RewardItem": "Item ID (if RewardType=1 or 2)",
                    "RewardAmount": "Item quantity (if RewardType=1 or 2)"
                }
            
                label_text = field
                if field in field_descriptions:
                    label_text = f"{field} - {field_descriptions[field]}"
            
                tk.Label(field_frame, text=label_text, 
                        bg=self.colors['card'], fg=self.colors['text'],
                        font=("Segoe UI", 8, "bold"), 
                        wraplength=300, justify=tk.LEFT).pack(anchor='w', pady=(0, 3))
            
                entry = tk.Entry(field_frame, font=("Segoe UI", 9),
                           bg=self.colors['white'], fg=self.colors['text'],
                           relief="solid", bd=1, highlightthickness=1,
                           highlightcolor=self.colors['secondary'],
                           insertbackground=self.colors['secondary'])
                entry.pack(fill=tk.X, pady=2, ipady=4)
            
                if values and field in values:
                    entry.insert(0, str(values[field]))
                entries[field] = entry
            
                self.add_entry_hover_effect(entry)

            def save():
                try:
                    data = {}
                    for k, e in entries.items():
                        value = e.get().strip()
                        if not value:
                            value = "0"
                        try:
                            data[k] = int(value)
                        except ValueError:
                            messagebox.showerror("Invalid Input", 
                                           f"Field '{k}' must be a valid integer.\nCurrent value: '{value}'",
                                           parent=popup)
                            return
            
                    # Validate reward data logic
                    if "RewardType" in data:
                        reward_type = data["RewardType"]
                        if reward_type == 0 and data.get("RewardMoney", 0) == 0:
                            if not messagebox.askyesno("Validation Warning", 
                                                 "RewardType is 0 (Money) but RewardMoney is 0.\nContinue anyway?",
                                                 parent=popup):
                                return
                        elif reward_type in [1, 2] and data.get("RewardItem", 0) == 0:
                            if not messagebox.askyesno("Validation Warning", 
                                                 "RewardType is for items but RewardItem is 0.\nContinue anyway?",
                                                 parent=popup):
                                return
                
                    cleanup_func()
                    callback(data)
                
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save data:\n{str(e)}", parent=popup)

            # Pack canvas
            canvas.pack(fill="both", expand=True)
        
            # Compact buttons
            cancel_btn = tk.Button(btn_container, text="❌ Cancel", command=cleanup_func,
                              bg=self.colors['muted'], fg=self.colors['white'], 
                              font=("Segoe UI", 8, "bold"),
                              relief="flat", bd=0, padx=15, pady=4,
                              cursor="hand2")
            cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
            save_btn = tk.Button(btn_container, text="✅ Save", command=save,
                            bg=self.colors['success'], fg=self.colors['white'], 
                            font=("Segoe UI", 8, "bold"),
                            relief="flat", bd=0, padx=15, pady=4,
                            cursor="hand2")
            save_btn.pack(side=tk.RIGHT)
        
            self.add_button_hover_effect(cancel_btn, self.colors['muted'])
            self.add_button_hover_effect(save_btn, self.colors['success'])
        
        except Exception as e:
            print(f"Error creating popup content: {e}")

    # Popup methods for conditions
    def add_condition_popup(self):
        try:
            self.open_popup("Add Condition", 
                           ["ConditionType", "ConditionId", "ConditionCount"], 
                           self.add_condition)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open condition popup:\n{str(e)}")

    def edit_condition_popup(self):
        try:
            selected = self.cond_tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a condition to edit.")
                return
            
            item = selected[0]
            idx = self.cond_tree.index(item)
            if 0 <= idx < len(self.conditions_data):
                self.open_popup("Edit Condition", 
                               ["ConditionType", "ConditionId", "ConditionCount"], 
                               lambda data: self.edit_condition_data(data, idx), 
                               self.conditions_data[idx])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit condition:\n{str(e)}")

    def edit_condition_data(self, data, idx):
        try:
            if 0 <= idx < len(self.conditions_data):
                self.conditions_data[idx] = data
                children = self.cond_tree.get_children()
                if idx < len(children):
                    item = children[idx]
                    self.cond_tree.item(item, values=tuple(data.values()))
                self.update_auto_counts()
                self.update_tab_counts()
                self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update condition:\n{str(e)}")

    def add_condition(self, data):
        try:
            self.conditions_data.append(data)
            self.cond_tree.insert("", tk.END, values=tuple(data.values()))
            self.update_auto_counts()
            self.update_tab_counts()
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add condition:\n{str(e)}")

    def delete_condition(self): 
        try:
            self.delete_data(self.conditions_data, self.cond_tree, "condition")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete condition:\n{str(e)}")

    # Popup methods for goals
    def add_goal_popup(self):
        try:
            self.open_popup("Add Goal", 
                           ["GoalType", "GoalId", "GoalCount", "goalAmount", "CurTypeCount", "SubValue", "SubValue1"], 
                           self.add_goal)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open goal popup:\n{str(e)}")

    def edit_goal_popup(self):
        try:
            selected = self.goal_tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a goal to edit.")
                return
            
            item = selected[0]
            idx = self.goal_tree.index(item)
            if 0 <= idx < len(self.goals_data):
                self.open_popup("Edit Goal", 
                               ["GoalType", "GoalId", "GoalCount", "goalAmount", "CurTypeCount", "SubValue", "SubValue1"], 
                               lambda data: self.edit_goal_data(data, idx), 
                               self.goals_data[idx])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit goal:\n{str(e)}")

    def edit_goal_data(self, data, idx):
        try:
            if 0 <= idx < len(self.goals_data):
                self.goals_data[idx] = data
                children = self.goal_tree.get_children()
                if idx < len(children):
                    item = children[idx]
                    self.goal_tree.item(item, values=tuple(data.values()))
                self.update_auto_counts()
                self.update_tab_counts()
                self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update goal:\n{str(e)}")

    def add_goal(self, data):
        try:
            self.goals_data.append(data)
            self.goal_tree.insert("", tk.END, values=tuple(data.values()))
            self.update_auto_counts()
            self.update_tab_counts()
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add goal:\n{str(e)}")

    def delete_goal(self): 
        try:
            self.delete_data(self.goals_data, self.goal_tree, "goal")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete goal:\n{str(e)}")

    # Popup methods for rewards
    def add_reward_popup(self):
        try:
            self.open_popup("Add Reward", 
                           ["Reward", "RewardType", "RewardMoney", "RewardItem", "RewardAmount"], 
                           self.add_reward)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open reward popup:\n{str(e)}")

    def edit_reward_popup(self):
        try:
            selected = self.reward_tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a reward to edit.")
                return
            
            item = selected[0]
            idx = self.reward_tree.index(item)
            if 0 <= idx < len(self.rewards_data):
                self.open_popup("Edit Reward", 
                               ["Reward", "RewardType", "RewardMoney", "RewardItem", "RewardAmount"], 
                               lambda data: self.edit_reward_data(data, idx), 
                               self.rewards_data[idx])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit reward popup:\n{str(e)}")

    def edit_reward_data(self, data, idx):
        try:
            if 0 <= idx < len(self.rewards_data):
                self.rewards_data[idx] = data
                children = self.reward_tree.get_children()
                if idx < len(children):
                    item = children[idx]
                    self.reward_tree.item(item, values=tuple(data.values()))
                self.update_auto_counts()
                self.update_tab_counts()
                self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update reward:\n{str(e)}")

    def add_reward(self, data):
        try:
            self.rewards_data.append(data)
            self.reward_tree.insert("", tk.END, values=tuple(data.values()))
            self.update_auto_counts()
            self.update_tab_counts()
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add reward:\n{str(e)}")

    def delete_reward(self): 
        try:
            self.delete_data(self.rewards_data, self.reward_tree, "reward")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete reward:\n{str(e)}")

    def delete_data(self, data_list, treeview, item_type):
        """Delete data with confirmation"""
        try:
            selected = treeview.selection()
            if not selected:
                messagebox.showwarning("No Selection", f"Please select a {item_type} to delete.")
                return
            
            if messagebox.askyesno("Confirm Delete", 
                                  f"Are you sure you want to delete this {item_type}?",
                                  icon='warning'):
                idx = treeview.index(selected[0])
                if 0 <= idx < len(data_list):
                    del data_list[idx]
                    treeview.delete(selected[0])
                    self.update_auto_counts()
                    self.update_tab_counts()
                    self.update_preview()
        except Exception as e:
            raise Exception(f"Failed to delete {item_type}: {str(e)}")

def main():
    """Main function to run the compact application"""
    try:
        root = tk.Tk()
        app = QuestXMLApp(root)
    
        # Center the window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
    
        root.mainloop()
    
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
