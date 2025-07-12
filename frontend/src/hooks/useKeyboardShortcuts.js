import { useEffect } from 'react';

const useKeyboardShortcuts = (shortcuts) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Check if user is typing in an input field
      const isTyping = ['INPUT', 'TEXTAREA'].includes(event.target.tagName);
      
      shortcuts.forEach(shortcut => {
        const { key, ctrl = false, alt = false, shift = false, callback, enabled = true } = shortcut;
        
        if (!enabled) return;
        
        // Don't trigger shortcuts when typing unless explicitly allowed
        if (isTyping && !shortcut.allowInInput) return;
        
        const isMatch = 
          event.key.toLowerCase() === key.toLowerCase() &&
          event.ctrlKey === ctrl &&
          event.altKey === alt &&
          event.shiftKey === shift;
          
        if (isMatch) {
          event.preventDefault();
          callback();
        }
      });
    };
    
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [shortcuts]);
};

export default useKeyboardShortcuts;