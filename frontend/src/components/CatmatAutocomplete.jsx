import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';

export default function CatmatAutocomplete({ value, onChange, error, itemType }) {
  const [query, setQuery] = useState(value || '');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef(null);

  useEffect(() => {
    setQuery(value || '');
  }, [value]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (query.length < 3) {
      setResults([]);
      return;
    }
    const delayDebounceFn = setTimeout(async () => {
      setLoading(true);
      try {
        const tipo = itemType === 'BEM' ? 'M' : 'S';
        const res = await api.get(`/catmat-search/?q=${query}&tipo=${tipo}`);
        setResults(res.data.resultado || []);
        setIsOpen(true);
      } catch (err) {
        console.error('Erro ao buscar catmat', err);
      } finally {
        setLoading(false);
      }
    }, 500);
    return () => clearTimeout(delayDebounceFn);
  }, [query, itemType]);

  return (
    <div ref={wrapperRef} className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => { setQuery(e.target.value); onChange(e.target.value); }}
        onFocus={() => { if (results.length > 0) setIsOpen(true); }}
        className={`w-full bg-slate-800 border ${error ? 'border-red-500' : 'border-slate-700'} text-slate-200 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500`}
        placeholder="Ex: CATSER 3220 (digite para buscar)"
      />
      {loading && <div className="absolute right-2 top-2 text-xs text-blue-400">Buscando...</div>}
      {isOpen && results.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-slate-800 border border-slate-700 rounded shadow-lg max-h-60 overflow-auto">
          {results.map((item, idx) => (
            <div
              key={idx}
              onClick={() => {
                const val = `${item.tipo === 'M' ? 'CATMAT' : 'CATSER'} ${item.codigo} - ${item.descricao}`;
                setQuery(val);
                onChange(val);
                setIsOpen(false);
              }}
              className="px-3 py-2 text-xs text-slate-300 hover:bg-slate-700 cursor-pointer border-b border-slate-700/50"
            >
              <span className="font-bold text-blue-400">{item.tipo === 'M' ? 'CATMAT' : 'CATSER'} {item.codigo}</span> - {item.descricao}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
