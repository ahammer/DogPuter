/**
 * DogPuter Web Interface JavaScript
 * 
 * This script handles all client-side functionality for the DogPuter web interface,
 * including command mapping management and video uploads.
 */

// Toast notification system
const Toast = {
    container: null,
    
    init() {
        // Create toast container if it doesn't exist
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },
    
    show(message, type = 'success', duration = 3000) {
        this.init();
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Create content
        const content = document.createElement('div');
        content.className = 'toast-content';
        content.textContent = message;
        
        // Create close button
        const close = document.createElement('div');
        close.className = 'toast-close';
        close.innerHTML = '&times;';
        close.addEventListener('click', () => {
            this.container.removeChild(toast);
        });
        
        // Assemble and show toast
        toast.appendChild(content);
        toast.appendChild(close);
        this.container.appendChild(toast);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentNode === this.container) {
                this.container.removeChild(toast);
            }
        }, duration);
    }
};

// App state
const State = {
    actions: [],
    mappings: {},
    configFiles: [],
    currentConfig: 'development.json',
    draggedAction: null
};

// API service
const Api = {
    async getActions() {
        try {
            const response = await fetch('/api/actions');
            const data = await response.json();
            return data.actions || [];
        } catch (error) {
            console.error('Error fetching actions:', error);
            Toast.show('Failed to load available actions', 'error');
            return [];
        }
    },
    
    async getConfigFiles() {
        try {
            const response = await fetch('/api/configs');
            const data = await response.json();
            return data.configs || [];
        } catch (error) {
            console.error('Error fetching config files:', error);
            Toast.show('Failed to load configuration files', 'error');
            return [];
        }
    },
    
    async getMappings(config = State.currentConfig) {
        try {
            const response = await fetch(`/api/mappings?config=${config}`);
            const data = await response.json();
            return data.mappings || {};
        } catch (error) {
            console.error('Error fetching mappings:', error);
            Toast.show('Failed to load key mappings', 'error');
            return {};
        }
    },
    
    async saveMappings(mappings, config = State.currentConfig) {
        try {
            const response = await fetch('/api/mappings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    mappings,
                    config
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                Toast.show('Mappings saved successfully', 'success');
                return true;
            } else {
                Toast.show(data.error || 'Failed to save mappings', 'error');
                return false;
            }
        } catch (error) {
            console.error('Error saving mappings:', error);
            Toast.show('Failed to save mappings', 'error');
            return false;
        }
    },
    
    async uploadVideo(file, onProgress) {
        try {
            const formData = new FormData();
            formData.append('video', file);
            
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                
                xhr.upload.addEventListener('progress', (event) => {
                    if (event.lengthComputable) {
                        const progress = (event.loaded / event.total) * 100;
                        if (onProgress) onProgress(progress);
                    }
                });
                
                xhr.addEventListener('load', () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            const response = JSON.parse(xhr.responseText);
                            resolve(response);
                        } catch (e) {
                            reject(new Error('Invalid response from server'));
                        }
                    } else {
                        try {
                            const error = JSON.parse(xhr.responseText);
                            reject(new Error(error.error || 'Upload failed'));
                        } catch (e) {
                            reject(new Error(`Upload failed with status ${xhr.status}`));
                        }
                    }
                });
                
                xhr.addEventListener('error', () => {
                    reject(new Error('Network error occurred'));
                });
                
                xhr.open('POST', '/api/upload', true);
                xhr.send(formData);
            });
        } catch (error) {
            console.error('Error uploading video:', error);
            throw error;
        }
    }
};

// UI components
const UI = {
    // Tab navigation
    initTabs() {
        const tabLinks = document.querySelectorAll('.tab-link');
        
        tabLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Get target tab ID
                const targetId = link.getAttribute('href');
                
                // Hide all tabs and remove active class from links
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                document.querySelectorAll('.tab-link').forEach(tabLink => {
                    tabLink.parentElement.classList.remove('active');
                });
                
                // Show target tab and set active class on link
                document.querySelector(targetId).classList.add('active');
                link.parentElement.classList.add('active');
            });
        });
    },
    
    // Actions list
    renderActions() {
        const actionsList = document.getElementById('actions-list');
        actionsList.innerHTML = '';
        
        // Sort actions by mapped status and name
        const sortedActions = [...State.actions].sort((a, b) => {
            // First by mapped status (unmapped first)
            if (a.mapped !== b.mapped) {
                return a.mapped ? 1 : -1;
            }
            // Then by name
            return a.name.localeCompare(b.name);
        });
        
        // Add each action
        sortedActions.forEach(action => {
            const template = document.getElementById('action-card-template');
            const card = template.content.cloneNode(true).querySelector('.action-card');
            
            card.dataset.command = action.name;
            card.classList.add(action.mapped ? 'mapped' : 'unmapped');
            
            const nameElement = card.querySelector('.action-name');
            nameElement.textContent = action.name;
            
            const mappingsElement = card.querySelector('.action-mappings');
            if (action.mappings && action.mappings.length > 0) {
                mappingsElement.textContent = 'Mapped to: ';
                action.mappings.forEach(key => {
                    const span = document.createElement('span');
                    span.textContent = key;
                    mappingsElement.appendChild(span);
                });
            } else {
                mappingsElement.textContent = 'Not mapped';
            }
            
            // Drag and drop handling
            card.addEventListener('dragstart', (e) => {
                State.draggedAction = action.name;
                card.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', action.name);
            });
            
            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
                State.draggedAction = null;
            });
            
            actionsList.appendChild(card);
        });
    },
    
    // Keyboard layout
    renderKeyboard() {
        const keyboard = document.getElementById('keyboard');
        keyboard.innerHTML = '';
        
        // Define keyboard layout (rows of keys)
        const keyboardLayout = [
            // Number row
            ['K_ESC', 'K_F1', 'K_F2', 'K_F3', 'K_F4', 'K_F5', 'K_F6', 'K_F7', 'K_F8', 'K_F9', 'K_F10', 'K_F11', 'K_F12'],
            ['K_BACKQUOTE', 'K_1', 'K_2', 'K_3', 'K_4', 'K_5', 'K_6', 'K_7', 'K_8', 'K_9', 'K_0', 'K_MINUS', 'K_EQUALS', 'K_BACKSPACE'],
            ['K_TAB', 'K_q', 'K_w', 'K_e', 'K_r', 'K_t', 'K_y', 'K_u', 'K_i', 'K_o', 'K_p', 'K_LEFTBRACKET', 'K_RIGHTBRACKET', 'K_BACKSLASH'],
            ['K_CAPSLOCK', 'K_a', 'K_s', 'K_d', 'K_f', 'K_g', 'K_h', 'K_j', 'K_k', 'K_l', 'K_SEMICOLON', 'K_QUOTE', 'K_RETURN'],
            ['K_LSHIFT', 'K_z', 'K_x', 'K_c', 'K_v', 'K_b', 'K_n', 'K_m', 'K_COMMA', 'K_PERIOD', 'K_SLASH', 'K_RSHIFT'],
            ['K_LCTRL', 'K_LALT', 'K_SPACE', 'K_RALT', 'K_RCTRL'],
            // Arrow keys
            ['K_UP'],
            ['K_LEFT', 'K_DOWN', 'K_RIGHT'],
            // Numpad
            ['K_KP7', 'K_KP8', 'K_KP9'],
            ['K_KP4', 'K_KP5', 'K_KP6'],
            ['K_KP1', 'K_KP2', 'K_KP3'],
            ['K_KP0', 'K_KP_PERIOD']
        ];
        
        // Create friendly names for keys
        const keyNames = {
            'K_ESC': 'Esc',
            'K_F1': 'F1', 'K_F2': 'F2', 'K_F3': 'F3', 'K_F4': 'F4',
            'K_F5': 'F5', 'K_F6': 'F6', 'K_F7': 'F7', 'K_F8': 'F8',
            'K_F9': 'F9', 'K_F10': 'F10', 'K_F11': 'F11', 'K_F12': 'F12',
            'K_BACKQUOTE': '`', 'K_MINUS': '-', 'K_EQUALS': '=', 'K_BACKSPACE': '←',
            'K_TAB': 'Tab', 'K_LEFTBRACKET': '[', 'K_RIGHTBRACKET': ']', 'K_BACKSLASH': '\\',
            'K_CAPSLOCK': 'Caps', 'K_SEMICOLON': ';', 'K_QUOTE': "'", 'K_RETURN': 'Enter',
            'K_LSHIFT': 'Shift', 'K_COMMA': ',', 'K_PERIOD': '.', 'K_SLASH': '/', 'K_RSHIFT': 'Shift',
            'K_LCTRL': 'Ctrl', 'K_LALT': 'Alt', 'K_SPACE': 'Space', 'K_RALT': 'Alt', 'K_RCTRL': 'Ctrl',
            'K_UP': '↑', 'K_DOWN': '↓', 'K_LEFT': '←', 'K_RIGHT': '→',
            'K_KP0': 'Num 0', 'K_KP1': 'Num 1', 'K_KP2': 'Num 2', 'K_KP3': 'Num 3',
            'K_KP4': 'Num 4', 'K_KP5': 'Num 5', 'K_KP6': 'Num 6', 'K_KP7': 'Num 7',
            'K_KP8': 'Num 8', 'K_KP9': 'Num 9', 'K_KP_PERIOD': 'Num .'
        };
        
        // Flatten array and create unique keys
        const keys = new Set();
        keyboardLayout.flat().forEach(key => keys.add(key));
        
        // Add each key
        keyboardLayout.forEach(row => {
            const rowDiv = document.createElement('div');
            rowDiv.className = 'keyboard-row';
            rowDiv.style.display = 'contents';
            
            row.forEach(keyCode => {
                const template = document.getElementById('keyboard-key-template');
                const key = template.content.cloneNode(true).querySelector('.key');
                
                key.dataset.key = keyCode;
                
                const keyName = key.querySelector('.key-name');
                keyName.textContent = keyNames[keyCode] || keyCode.replace('K_', '');
                
                const keyCommand = key.querySelector('.key-command');
                
                // Check if key has a command
                if (State.mappings[keyCode]) {
                    key.classList.add('has-command');
                    keyCommand.textContent = State.mappings[keyCode];
                    
                    // Add remove button
                    const removeBtn = document.createElement('span');
                    removeBtn.className = 'remove-mapping';
                    removeBtn.innerHTML = '&times;';
                    removeBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        delete State.mappings[keyCode];
                        UI.renderKeyboard();
                        UI.renderActions();
                    });
                    
                    keyCommand.appendChild(removeBtn);
                }
                
                // Drop handling
                key.addEventListener('dragover', (e) => {
                    if (State.draggedAction) {
                        e.preventDefault();
                        key.classList.add('drag-over');
                    }
                });
                
                key.addEventListener('dragleave', () => {
                    key.classList.remove('drag-over');
                });
                
                key.addEventListener('drop', (e) => {
                    e.preventDefault();
                    key.classList.remove('drag-over');
                    
                    if (State.draggedAction) {
                        // Assign action to key
                        State.mappings[keyCode] = State.draggedAction;
                        UI.renderKeyboard();
                        UI.renderActions();
                    }
                });
                
                rowDiv.appendChild(key);
            });
            
            keyboard.appendChild(rowDiv);
        });
    },
    
    // Config file selector
    renderConfigSelector() {
        const select = document.getElementById('config-file');
        select.innerHTML = '';
        
        State.configFiles.forEach(config => {
            const option = document.createElement('option');
            option.value = config;
            option.textContent = config;
            
            if (config === State.currentConfig) {
                option.selected = true;
            }
            
            select.appendChild(option);
        });
        
        // Handle config change
        select.addEventListener('change', async () => {
            State.currentConfig = select.value;
            await App.loadMappings();
            UI.renderKeyboard();
            UI.renderActions();
        });
    },
    
    // Upload area
    initUploadArea() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        const uploadList = document.getElementById('upload-list');
        
        // Click to select files
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Handle file selection
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                handleFiles(fileInput.files);
            }
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            if (e.dataTransfer.files.length > 0) {
                handleFiles(e.dataTransfer.files);
            }
        });
        
        // Handle files function
        function handleFiles(files) {
            const validFiles = Array.from(files).filter(file => 
                file.type === 'video/mp4' || file.name.endsWith('.mp4')
            );
            
            if (validFiles.length === 0) {
                Toast.show('Please select MP4 video files only', 'error');
                return;
            }
            
            // Process each file
            validFiles.forEach(async (file) => {
                // Check if filename is in command_name.mp4 format
                const filename = file.name;
                
                // Create upload item in list
                const template = document.getElementById('upload-item-template');
                const item = template.content.cloneNode(true).querySelector('.upload-item');
                
                const nameElement = item.querySelector('.upload-item-name');
                nameElement.textContent = filename;
                
                const statusElement = item.querySelector('.upload-item-status');
                statusElement.textContent = 'Uploading...';
                
                const progressBar = item.querySelector('.progress-bar');
                
                uploadList.appendChild(item);
                
                try {
                    // Upload the file
                    const result = await Api.uploadVideo(file, (progress) => {
                        progressBar.style.width = `${progress}%`;
                    });
                    
                    // Update status on success
                    statusElement.textContent = 'Uploaded';
                    statusElement.classList.add('success');
                    progressBar.style.width = '100%';
                    
                    // Refresh actions list
                    await App.loadActions();
                    UI.renderActions();
                    
                    Toast.show(`File ${filename} uploaded successfully`, 'success');
                } catch (error) {
                    // Update status on error
                    statusElement.textContent = error.message || 'Failed';
                    statusElement.classList.add('error');
                    
                    Toast.show(`Failed to upload ${filename}: ${error.message}`, 'error');
                }
            });
            
            // Clear file input
            fileInput.value = '';
        }
    },
    
    // Save mappings button
    initSaveButton() {
        const saveButton = document.getElementById('save-mappings');
        
        saveButton.addEventListener('click', async () => {
            const result = await Api.saveMappings(State.mappings, State.currentConfig);
            
            if (result) {
                // Refresh actions to show updated mappings
                await App.loadActions();
                UI.renderActions();
            }
        });
    }
};

// Main application
const App = {
    async init() {
        // Initialize UI components
        UI.initTabs();
        UI.initUploadArea();
        UI.initSaveButton();
        
        // Load data
        await Promise.all([
            this.loadConfigFiles(),
            this.loadActions(),
            this.loadMappings()
        ]);
        
        // Render UI with loaded data
        UI.renderConfigSelector();
        UI.renderKeyboard();
        UI.renderActions();
        
        console.log('DogPuter web interface initialized');
    },
    
    async loadConfigFiles() {
        State.configFiles = await Api.getConfigFiles();
        if (State.configFiles.length > 0 && !State.configFiles.includes(State.currentConfig)) {
            State.currentConfig = State.configFiles[0];
        }
    },
    
    async loadActions() {
        State.actions = await Api.getActions();
    },
    
    async loadMappings() {
        State.mappings = await Api.getMappings(State.currentConfig);
    }
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
