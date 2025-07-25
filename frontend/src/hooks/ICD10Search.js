// hooks/useICD10Search.js
import { useState, useEffect, useCallback, useRef } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useICD10Search = (initialQuery = '', options = {}) => {
  const {
    minLength = 2,
    debounceMs = 300,
    maxResults = 10,
    enabled = true
  } = options;

  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTime, setSearchTime] = useState(null);
  
  const abortControllerRef = useRef(null);
  const debounceTimerRef = useRef(null);

  const searchICD10 = useCallback(async (searchQuery) => {
    console.log('Searching ICD10 for:', searchQuery, 'minLength:', minLength, 'enabled:', enabled);
    
    if (!searchQuery || searchQuery.trim().length < minLength || !enabled) {
      console.log('Search skipped - query too short or disabled');
      setResults([]);
      setLoading(false);
      setError(null);
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setLoading(true);
    setError(null);

    try {
      console.log('Making API request to:', `${API_BASE_URL}/api/v1/icd10`);
      
      const url = new URL(`${API_BASE_URL}/api/v1/icd10`);
      url.searchParams.set('q', searchQuery.trim());
      url.searchParams.set('limit', maxResults.toString());

      console.log('Full URL:', url.toString());

      const startTime = performance.now();
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        signal: abortControllerRef.current.signal,
      });

      console.log('API Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error response:', errorText);
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      const endTime = performance.now();
      
      console.log('API Response data:', data);
      console.log('Search completed in:', endTime - startTime, 'ms');
      
      // Handle different response formats
      let codes = [];
      if (Array.isArray(data)) {
        codes = data;
      } else if (data.codes && Array.isArray(data.codes)) {
        codes = data.codes;
      } else if (data.results && Array.isArray(data.results)) {
        codes = data.results;
      }
      
      setResults(codes);
      setSearchTime(data.search_time_ms || Math.round(endTime - startTime));
      setLoading(false);
      
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Search request aborted');
        return;
      }
      
      console.error('ICD-10 search error:', err);
      setError(`Search failed: ${err.message}`);
      setResults([]);
      setLoading(false);
    }
  }, [minLength, maxResults, enabled]);

  // Debounced search effect
  useEffect(() => {
    console.log('Query changed to:', query, 'Will search after', debounceMs, 'ms');
    
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    
    debounceTimerRef.current = setTimeout(() => {
      console.log('Debounce timer fired, calling searchICD10');
      searchICD10(query);
    }, debounceMs);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query, searchICD10, debounceMs]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  const searchNow = useCallback((searchQuery) => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    searchICD10(searchQuery || query);
  }, [searchICD10, query]);

  const getCodeDetails = useCallback(async (code) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/icd10/${encodeURIComponent(code)}`, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (err) {
      console.error('Error fetching ICD-10 code details:', err);
      throw err;
    }
  }, []);

  return {
    query,
    setQuery,
    results,
    loading,
    error,
    searchTime,
    searchNow,
    getCodeDetails
  };
};