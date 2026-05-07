import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Printer as PrinterIcon, RefreshCw, Calendar as CalendarIcon, Hash, Percent, TrendingDown, Copy, FileText, Layers, Droplet, Activity, Server, MapPin, CalendarDays, X } from 'lucide-react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { format } from 'date-fns';

interface PrinterStatus {
  db_id: number;
  name: string;
  ip: string;
  status: string;
  serial: string;
  location: string;
  page_count: number;
  copied_count: number;
  printed_count: number;
  toner_percent: number;
  toner_install_date: string;
  daily_total: number;
  daily_copied: number;
  daily_printed: number;
  daily_toner_drop: number;
}

function App() {
  const [printers, setPrinters] = useState<PrinterStatus[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newName, setNewName] = useState('');
  const [newIp, setNewIp] = useState('');
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [selectedPrinterHistory, setSelectedPrinterHistory] = useState<PrinterStatus | null>(null);
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [calendarDate, setCalendarDate] = useState<Date>(new Date());

  const API_URL = 'http://localhost:8000';

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/printers/status`);
      setPrinters(response.data);
    } catch (error) {
      console.error("Error fetching status", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3600000); // 1 hora
    return () => clearInterval(interval);
  }, []);

  const handleAddPrinter = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/printers?name=${newName}&ip_address=${newIp}`);
      setNewName(''); setNewIp(''); setShowAddForm(false);
      fetchStatus();
    } catch (error) { alert("Error al agregar impresora."); }
  };

  const handleOpenHistory = async (printer: PrinterStatus) => {
    setSelectedPrinterHistory(printer);
    setCalendarDate(new Date());
    setHistoryModalOpen(true);
    try {
      const response = await axios.get(`${API_URL}/printers/${printer.db_id}/history`);
      setHistoryData(response.data);
    } catch (error) {
      console.error("Error fetching history", error);
    }
  };

  console.log(printers);

  return (
    <div className="relative min-h-screen bg-[#0B0F19] font-sans overflow-x-hidden text-slate-300 selection:bg-indigo-500/30">
      {/* Animated Background Orbs */}
      <div className="fixed top-[-10%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-blue-900/20 blur-[150px] mix-blend-screen pointer-events-none animate-float"></div>
      <div className="fixed bottom-[-10%] right-[-10%] w-[40vw] h-[40vw] rounded-full bg-indigo-900/20 blur-[120px] mix-blend-screen pointer-events-none animate-float" style={{ animationDelay: '2s' }}></div>

      <div className="relative z-10 p-4 md:p-8">
        <header className="max-w-7xl mx-auto mb-12 mt-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-bold uppercase tracking-widest mb-3 border border-indigo-500/20">
              <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse shadow-[0_0_8px_rgba(99,102,241,0.8)]"></span>
              Monitoreo Activo
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 tracking-tight flex items-center gap-4">
              <div className="p-3 bg-white/5 backdrop-blur-md shadow-lg shadow-black/50 rounded-2xl border border-white/10">
                <PrinterIcon className="text-indigo-400" size={36} />
              </div>
              Xerox Dashboard
            </h1>
            <p className="text-slate-500 mt-3 text-lg font-medium max-w-xl">Panel de control de consumibles e historial volumétrico en tiempo real.</p>
          </div>

          <div className="flex flex-wrap gap-3 w-full md:w-auto">
            <button onClick={fetchStatus} disabled={loading} className="flex-1 md:flex-none flex items-center justify-center gap-2 bg-white/5 backdrop-blur-md border border-white/10 px-6 py-3 rounded-2xl hover:bg-white/10 transition-all shadow-lg font-semibold text-white group disabled:opacity-50">
              <RefreshCw size={18} className={`text-slate-400 group-hover:text-indigo-400 transition-colors ${loading ? 'animate-spin text-indigo-400' : ''}`} />
              <span>Actualizar</span>
            </button>
            <button onClick={() => setShowAddForm(true)} className="flex-1 md:flex-none flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-blue-600 text-white px-6 py-3 rounded-2xl hover:shadow-[0_0_20px_rgba(79,70,229,0.4)] transition-all font-semibold hover:-translate-y-0.5 border border-indigo-500/50">
              <Plus size={20} /> Nueva Impresora
            </button>
          </div>
        </header>

        <main className="max-w-7xl mx-auto">
          {showAddForm && (
            <div className="mb-10 p-1 rounded-3xl bg-gradient-to-br from-indigo-500/30 to-blue-500/10 animate-in fade-in slide-in-from-top-4 duration-300">
              <div className="bg-[#131826] border border-white/10 p-6 md:p-8 rounded-[1.4rem] shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400">
                    <Plus size={20} />
                  </div>
                  <h2 className="text-xl font-bold text-white">Registrar Nuevo Equipo</h2>
                </div>
                <form onSubmit={handleAddPrinter} className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1 relative">
                    <input type="text" placeholder="Nombre (Ej. Recepción)" className="w-full bg-[#0B0F19] border border-white/10 px-5 py-4 rounded-2xl focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all text-white placeholder:text-slate-600 font-medium" value={newName} onChange={(e) => setNewName(e.target.value)} required />
                  </div>
                  <div className="flex-1 relative">
                    <input type="text" placeholder="Dirección IP (Ej. 10.30.20.102)" className="w-full bg-[#0B0F19] border border-white/10 px-5 py-4 rounded-2xl focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all text-white placeholder:text-slate-600 font-mono text-sm" value={newIp} onChange={(e) => setNewIp(e.target.value)} required />
                  </div>
                  <div className="flex gap-2">
                    <button type="submit" className="bg-white text-black px-8 py-4 rounded-2xl hover:bg-slate-200 font-bold transition-all shadow-lg hover:shadow-xl">Guardar</button>
                    <button type="button" onClick={() => setShowAddForm(false)} className="bg-white/5 text-white border border-white/10 px-6 py-4 rounded-2xl hover:bg-white/10 font-bold transition-all">Cancelar</button>
                  </div>
                </form>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 md:gap-8">
            {printers.map((printer) => {
              const isOnline = printer.status === 'Online';
              const isLowToner = printer.toner_percent <= 15;

              return (
                <div key={printer.db_id} className="group relative bg-[#131826]/80 backdrop-blur-xl border border-white/5 rounded-3xl overflow-hidden hover:-translate-y-1 hover:shadow-[0_10px_40px_-10px_rgba(0,0,0,0.5)] hover:border-white/10 transition-all duration-300">
                  <div className={`absolute top-0 left-0 w-full h-1 ${isOnline ? 'bg-gradient-to-r from-emerald-400 to-teal-500' : 'bg-gradient-to-r from-rose-500 to-red-600'}`}></div>

                  <div className="p-7">
                    <div className="flex justify-between items-start mb-6">
                      <div className="pr-4">
                        <h3 className="text-2xl font-black text-white tracking-tight mb-2 group-hover:text-indigo-400 transition-colors">{printer.name}</h3>
                        <div className="flex flex-col gap-1 text-sm text-slate-400">
                          <div className="flex items-center gap-2">
                            <Server size={14} className="text-slate-500" />
                            <span className="font-mono text-slate-300">IP: {printer.ip}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Hash size={14} className="text-slate-500" />
                            <span className="font-mono text-slate-300">N/S: {printer.serial}</span>
                          </div>
                          {printer.location && printer.location !== 'N/A' && (
                            <div className="flex items-center gap-2">
                              <MapPin size={14} className="text-slate-500" />
                              <span className="font-mono text-slate-300">Lugar: {printer.location}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className={`shrink-0 px-3 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest border ${isOnline ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                        {printer.status}
                      </div>
                    </div>

                    <div className="space-y-6">
                      <div className="bg-[#0B0F19] p-5 rounded-2xl border border-white/5 shadow-inner relative overflow-hidden">
                        {isLowToner && <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/20 rounded-bl-full -z-10 blur-2xl"></div>}

                        <div className="flex justify-between items-center mb-3">
                          <div className="flex items-center gap-2">
                            <div className={`p-1.5 rounded-lg ${isLowToner ? 'bg-rose-500/20 text-rose-400' : 'bg-indigo-500/20 text-indigo-400'}`}>
                              <Droplet size={16} />
                            </div>
                            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Nivel de Tóner</span>
                          </div>
                          <span className={`text-2xl font-black ${isLowToner ? 'text-rose-400' : 'text-white'}`}>{printer.toner_percent}%</span>
                        </div>

                        <div className="w-full bg-white/5 rounded-full h-3 mb-4 overflow-hidden border border-white/5">
                          <div
                            className={`h-full rounded-full transition-all duration-1000 ease-out relative ${isLowToner ? 'bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.8)]' : 'bg-gradient-to-r from-indigo-500 to-blue-400 shadow-[0_0_10px_rgba(99,102,241,0.5)]'}`}
                            style={{ width: `${printer.toner_percent}%` }}
                          >
                            <div className="absolute inset-0 bg-white/20 w-full" style={{ animation: 'shimmer 2s infinite' }}></div>
                          </div>
                        </div>

                        <div className="flex flex-col gap-2">
                          <div className="flex items-center justify-between text-[11px] font-medium text-slate-400 bg-white/5 px-3 py-2 rounded-xl border border-white/5">
                            <div className="flex items-center gap-1.5">
                              <CalendarIcon size={12} className="text-indigo-400" />
                              <span>Fecha Instalación:</span>
                            </div>
                            <span className="text-white font-semibold">{printer.toner_install_date}</span>
                          </div>

                          <div className="flex items-center justify-between text-[11px] font-medium text-slate-400 bg-white/5 px-3 py-2 rounded-xl border border-white/5">
                            <div className="flex items-center gap-1.5">
                              <TrendingDown size={12} className="text-rose-400" />
                              <span>Gasto de Tóner Hoy:</span>
                            </div>
                            <span className="text-white font-semibold">{printer.daily_toner_drop}%</span>
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-indigo-500/10 p-4 rounded-2xl border border-indigo-500/20 transition-all hover:bg-indigo-500/20">
                          <p className="text-[10px] uppercase font-bold text-indigo-300 tracking-widest mb-2 flex items-center gap-1.5">
                            <FileText size={12} /> Impresas Hoy
                          </p>
                          <span className="text-3xl font-black text-white tracking-tight">{printer.daily_printed}</span>
                        </div>
                        <div className="bg-blue-500/10 p-4 rounded-2xl border border-blue-500/20 transition-all hover:bg-blue-500/20">
                          <p className="text-[10px] uppercase font-bold text-blue-300 tracking-widest mb-2 flex items-center gap-1.5">
                            <Copy size={12} /> Copiadas Hoy
                          </p>
                          <span className="text-3xl font-black text-white tracking-tight">{printer.daily_copied}</span>
                        </div>
                      </div>

                      <div className="space-y-1 bg-white/5 p-4 rounded-2xl border border-white/5">
                        <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
                          <span className="text-xs font-medium text-slate-400 flex items-center gap-2"><FileText size={12} /> Hojas impresas totales</span>
                          <span className="font-semibold text-white font-inter">{printer.printed_count.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
                          <span className="text-xs font-medium text-slate-400 flex items-center gap-2"><Copy size={12} /> Hojas copiadas totales</span>
                          <span className="font-semibold text-white font-inter">{printer.copied_count.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center py-2 mt-1">
                          <span className="text-xs font-bold text-indigo-300 flex items-center gap-1.5"><Layers size={12} /> Gran Total Equipo</span>
                          <span className="text-sm font-black text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-md border border-indigo-500/20">{printer.page_count.toLocaleString()}</span>
                        </div>
                      </div>

                      <div className="pt-2">
                        <button onClick={() => handleOpenHistory(printer)} className="w-full py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl flex items-center justify-center gap-2 text-slate-300 hover:text-white transition-all font-semibold group/btn">
                          <CalendarDays size={18} className="text-indigo-400 group-hover/btn:scale-110 transition-transform" />
                          Histórico Diario
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {!loading && printers.length === 0 && (
            <div className="text-center py-20 bg-white/5 backdrop-blur-sm rounded-3xl border border-white/10 border-dashed">
              <PrinterIcon className="mx-auto text-slate-600 mb-4" size={48} />
              <h3 className="text-lg font-bold text-slate-300 mb-1">No hay equipos registrados</h3>
              <p className="text-slate-500 text-sm">Haz clic en "Nueva Impresora" para comenzar a monitorear.</p>
            </div>
          )}

          {historyModalOpen && selectedPrinterHistory && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
              <div className="bg-[#131826] border border-white/10 rounded-3xl p-6 w-full max-w-md shadow-2xl animate-in zoom-in-95 duration-200">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                      <CalendarDays className="text-indigo-400" />
                      Historial
                    </h3>
                    <p className="text-sm text-slate-400">{selectedPrinterHistory.name}</p>
                  </div>
                  <button onClick={() => setHistoryModalOpen(false)} className="p-2 hover:bg-white/10 rounded-full transition-colors text-slate-400 hover:text-white">
                    <X size={20} />
                  </button>
                </div>

                <div className="mb-6 custom-calendar-wrapper">
                  <Calendar 
                    onChange={(val) => setCalendarDate(val as Date)} 
                    value={calendarDate} 
                    className="w-full bg-[#0B0F19] rounded-2xl border-none text-white font-sans p-4 shadow-inner"
                    tileClassName={({ date }) => {
                      const dateStr = format(date, 'yyyy-MM-dd');
                      const hasData = historyData.some(d => d.date === dateStr);
                      return hasData ? 'has-data-tile' : '';
                    }}
                  />
                </div>

                {(() => {
                  const selectedDateStr = format(calendarDate, 'yyyy-MM-dd');
                  const selectedDayData = historyData.find(d => d.date === selectedDateStr);

                  return (
                    <div className="space-y-3">
                      <h4 className="text-sm font-semibold text-slate-300 mb-2 border-b border-white/10 pb-2">Datos del {format(calendarDate, 'dd/MM/yyyy')}</h4>
                      {selectedDayData ? (
                        <>
                          <div className="flex justify-between items-center bg-indigo-500/10 p-3 rounded-xl border border-indigo-500/20">
                            <span className="text-sm text-indigo-300 flex items-center gap-2"><FileText size={16} /> Impresas</span>
                            <span className="font-bold text-white text-lg">{selectedDayData.daily_printed}</span>
                          </div>
                          <div className="flex justify-between items-center bg-blue-500/10 p-3 rounded-xl border border-blue-500/20">
                            <span className="text-sm text-blue-300 flex items-center gap-2"><Copy size={16} /> Copiadas</span>
                            <span className="font-bold text-white text-lg">{selectedDayData.daily_copied}</span>
                          </div>
                          <div className="flex justify-between items-center bg-rose-500/10 p-3 rounded-xl border border-rose-500/20">
                            <span className="text-sm text-rose-300 flex items-center gap-2"><Droplet size={16} /> Tóner Gastado</span>
                            <span className="font-bold text-white text-lg">{selectedDayData.daily_toner_drop}%</span>
                          </div>
                        </>
                      ) : (
                        <div className="text-center py-6 text-slate-500 bg-white/5 rounded-xl border border-white/5">
                          <Activity className="mx-auto mb-2 opacity-50" size={24} />
                          <p className="text-sm">No hay actividad registrada para este día.</p>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </div>
            </div>
          )}
        </main>
      </div>

      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        /* Custom Calendar Styles */
        .custom-calendar-wrapper .react-calendar {
          background-color: #0B0F19 !important;
          border: 1px solid rgba(255, 255, 255, 0.1) !important;
          font-family: inherit !important;
          border-radius: 1rem;
        }
        .react-calendar__navigation button {
          color: white !important;
          min-width: 44px;
          background: none;
          font-size: 16px;
          margin-top: 8px;
          border-radius: 8px;
          padding: 8px;
        }
        .react-calendar__navigation button:enabled:hover,
        .react-calendar__navigation button:enabled:focus {
          background-color: rgba(255,255,255,0.1) !important;
        }
        .react-calendar__month-view__weekdays {
          color: #94a3b8 !important; /* slate-400 */
          text-transform: uppercase;
          font-weight: bold;
          font-size: 0.75rem;
          margin-bottom: 8px;
        }
        .react-calendar__month-view__weekdays__weekday abbr {
          text-decoration: none;
        }
        .react-calendar__tile {
          color: white !important;
          padding: 12px 6.6667px !important;
          border-radius: 8px;
          background: none;
        }
        .react-calendar__tile:enabled:hover,
        .react-calendar__tile:enabled:focus {
          background-color: rgba(99, 102, 241, 0.3) !important;
        }
        .react-calendar__tile--now {
          background-color: rgba(255, 255, 255, 0.1) !important;
          color: white !important;
        }
        .react-calendar__tile--active {
          background-color: #4f46e5 !important; /* indigo-600 */
          color: white !important;
        }
        .has-data-tile {
          position: relative;
        }
        .has-data-tile::after {
          content: '';
          position: absolute;
          bottom: 4px;
          left: 50%;
          transform: translateX(-50%);
          width: 4px;
          height: 4px;
          border-radius: 50%;
          background-color: #38bdf8; /* sky-400 */
        }
        .react-calendar__tile--active.has-data-tile::after {
          background-color: white;
        }
        .react-calendar__month-view__days__day--neighboringMonth {
          color: #475569 !important; /* slate-600 */
        }
      `}</style>
    </div>
  );
}

export default App;
