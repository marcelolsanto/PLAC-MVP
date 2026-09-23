import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';

export default function CatmatAutocomplete({ value, onChange, error, itemType }) {
  const [query, setQuery] = useState(value || '');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef(null);

  useEffect(() => {
    if (value !== query) {
        setQuery(value || '');
    }
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
    // Don't search again if the user already selected the item
    if (query.includes(' - ')) return;
    
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
    <div ref={wrapperRef} className="relative w-full">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
          <svg className="w-4 h-4 text-slate-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
          </svg>
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => { 
            setQuery(e.target.value); 
            onChange(e.target.value); 
          }}
          onFocus={() => { if (results.length > 0) setIsOpen(true); }}
          className={`w-full bg-[#1e1e1e] border ${error ? 'border-red-500' : 'border-slate-600'} text-slate-100 rounded-lg pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500`}
          placeholder="Ex: DESENVOLVIMENTO DE SOFTWARE"
        />
        {loading && (
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
             <span className="text-xs text-blue-400 animate-pulse">Buscando...</span>
          </div>
        )}
      </div>

      {isOpen && results.length > 0 && (
        <div className="absolute z-50 w-full mt-2 bg-[#1a1a1a] border border-slate-700 rounded-lg shadow-2xl max-h-[400px] overflow-y-auto p-3">
          <div className="text-xs text-slate-400 mb-3 px-1">{results.length} itens encontrados:</div>
          <div className="flex flex-col gap-2">
            {results.map((item, idx) => {
              const isMat = item.tipo === 'M';
              const badgeBg = isMat ? 'bg-orange-900/50 text-orange-300 border-orange-700/50' : 'bg-purple-900/50 text-purple-300 border-purple-700/50';
              const typeName = isMat ? 'CATMAT' : 'CATSER';
              
              // Simula um match aleatório baseado no tamanho (só para UI como no print)
              const match = Math.floor(75 + Math.random() * 24); 
              const matchColor = match > 90 ? 'text-emerald-400 border-emerald-900/50' : 'text-blue-400 border-blue-900/50';

              return (
                <div key={idx} className="border border-slate-700 bg-slate-800/30 rounded-lg p-3 hover:bg-slate-700/50 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 text-[11px] font-bold rounded border ${badgeBg}`}>
                        {typeName} #{item.codigo}
                      </span>
                      <span className={`px-2 py-0.5 text-[11px] font-medium rounded border bg-slate-900/50 flex items-center gap-1 ${matchColor}`}>
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        {match}% Match IA
                      </span>
                    </div>
                    <span className="text-slate-200 text-xs font-bold leading-tight">{item.descricao}</span>
                  </div>
                  
                  <button
                    type="button"
                    onClick={() => {
                      const val = `${typeName} ${item.codigo} - ${item.descricao}`;
                      setQuery(val);
                      onChange(val);
                      setIsOpen(false);
                    }}
                    className="shrink-0 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold py-1.5 px-4 rounded-md transition-colors flex items-center gap-1"
                  >
                    <span>+</span> Incluir
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
