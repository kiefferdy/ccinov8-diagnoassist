// components/ICD10Autocomplete.jsx
import React, { useState, useRef, useEffect } from 'react';
import { Search, Loader2, CheckCircle } from 'lucide-react';
import { useICD10Search } from "../../../hooks/ICD10Search";

export const ICD10Autocomplete = ({ 
  onSelect, 
  initialValue = '', 
  placeholder = 'Search ICD-10 codes...', 
  className = '',
  value,
  onChange 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [displayValue, setDisplayValue] = useState(value || initialValue);
  const inputRef = useRef(null);
  const listRef = useRef(null);
  
  const { 
    query, 
    setQuery, 
    results, 
    loading, 
    error,
    searchTime 
  } = useICD10Search('', {
    minLength: 2,
    debounceMs: 300,
    maxResults: 10,
    enabled: true
  });

  // Debug logging
  useEffect(() => {
    console.log('ICD10Autocomplete state:', {
      query,
      results: results?.length || 0,
      loading,
      error,
      displayValue,
      isOpen
    });
  }, [query, results, loading, error, displayValue, isOpen]);

  // Handle controlled/uncontrolled input
  useEffect(() => {
    if (value !== undefined && value !== displayValue) {
      console.log('Updating displayValue from prop:', value);
      setDisplayValue(value);
    }
  }, [value, displayValue]);

  useEffect(() => {
    if (initialValue && !value && !displayValue) {
      console.log('Setting initial value:', initialValue);
      setDisplayValue(initialValue);
    }
  }, [initialValue, value, displayValue]);

  const handleInputChange = (e) => {
    const inputValue = e.target.value;
    console.log('Input changed:', inputValue);
    
    setDisplayValue(inputValue);
    setSelectedIndex(-1);
    
    // Always update the search query
    setQuery(inputValue);
    
    // Open dropdown if we have enough characters
    if (inputValue.length >= 2) {
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
    
    // Call onChange if provided
    if (onChange) {
      onChange(inputValue);
    }
  };

  const handleSelect = (code) => {
    console.log('Code selected:', code);
    const selectedValue = `${code.code} - ${code.description}`;
    
    setDisplayValue(selectedValue);
    setIsOpen(false);
    setSelectedIndex(-1);
    
    // Don't update query after selection to avoid new search
    // setQuery(selectedValue);
    
    // Call callbacks
    if (onChange) {
      onChange(selectedValue);
    }
    if (onSelect) {
      onSelect(code);
    }
  };

  const handleKeyDown = (e) => {
    if (!isOpen || !results || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < results.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : results.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && results[selectedIndex]) {
          handleSelect(results[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const handleFocus = () => {
    console.log('Input focused, displayValue:', displayValue);
    // Extract search term from display value if it contains a selection
    const searchTerm = displayValue.includes(' - ') ? 
      displayValue.split(' - ')[0] : displayValue;
    
    if (searchTerm && searchTerm.length >= 2) {
      setQuery(searchTerm);
      setIsOpen(true);
    }
  };

  const handleBlur = (e) => {
    // Check if we're clicking on a dropdown item
    const relatedTarget = e.relatedTarget;
    const dropdown = e.currentTarget.closest('.relative')?.querySelector('[role="listbox"]');
    
    if (dropdown && dropdown.contains(relatedTarget)) {
      // Don't close if clicking on dropdown
      return;
    }
    
    // Delay hiding to allow clicks on dropdown items
    setTimeout(() => {
      setIsOpen(false);
      setSelectedIndex(-1);
    }, 150);
  };

  // Scroll selected item into view
  useEffect(() => {
    if (selectedIndex >= 0 && listRef.current && listRef.current.children[selectedIndex]) {
      const selectedElement = listRef.current.children[selectedIndex];
      selectedElement.scrollIntoView({
        block: 'nearest',
        behavior: 'smooth'
      });
    }
  }, [selectedIndex]);

  // Show dropdown when we have results
  useEffect(() => {
    if (results && results.length > 0 && query.length >= 2) {
      setIsOpen(true);
    }
  }, [results, query]);

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={displayValue || ''}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
          autoComplete="off"
        />
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          {loading ? (
            <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />
          ) : (
            <Search className="w-4 h-4 text-gray-400" />
          )}
        </div>
      </div>

      {isOpen && query.length >= 2 && (
        <div 
          role="listbox"
          className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-xl shadow-lg max-h-60 overflow-y-auto"
        >
          {error && (
            <div className="px-4 py-3 text-red-600 text-sm border-b">
              <span className="font-medium">Error:</span> {error}
            </div>
          )}
          
          {loading && (
            <div className="px-4 py-6 text-center text-gray-500">
              <Loader2 className="w-6 h-6 mx-auto mb-2 text-gray-300 animate-spin" />
              <p>Searching ICD-10 codes...</p>
            </div>
          )}
          
          {!loading && results && results.length > 0 && (
            <div ref={listRef}>
              {results.map((code, index) => (
                <button
                  key={`${code.code}-${index}`}
                  type="button"
                  role="option"
                  aria-selected={index === selectedIndex}
                  className={`w-full text-left px-4 py-3 hover:bg-purple-50 border-b border-gray-100 last:border-b-0 transition-colors duration-150 ${
                    index === selectedIndex ? 'bg-purple-50 border-purple-200' : ''
                  }`}
                  onMouseDown={(e) => {
                    // Prevent blur from firing before click
                    e.preventDefault();
                    handleSelect(code);
                  }}
                  onMouseEnter={() => setSelectedIndex(index)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-purple-700 truncate">
                        {code.code}
                      </div>
                      <div className="text-sm text-gray-700 mt-1 line-clamp-2">
                        {code.description}
                      </div>
                      {code.category && (
                        <div className="text-xs text-gray-500 mt-1 truncate">
                          {code.category}
                        </div>
                      )}
                    </div>
                    <CheckCircle className="w-4 h-4 text-gray-400 mt-1 flex-shrink-0 ml-2" />
                  </div>
                </button>
              ))}
              
              {searchTime && (
                <div className="px-4 py-2 text-xs text-gray-500 bg-gray-50 border-t">
                  Found {results.length} results in {searchTime}ms
                </div>
              )}
            </div>
          )}

          {!loading && (!results || results.length === 0) && query.length >= 2 && (
            <div className="px-4 py-6 text-center text-gray-500">
              <Search className="w-8 h-8 mx-auto mb-2 text-gray-300" />
              <p className="font-medium">No ICD-10 codes found</p>
              <p className="text-xs mt-1">Try a different search term</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ICD10Autocomplete;