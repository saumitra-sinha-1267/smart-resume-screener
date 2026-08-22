import React from 'react';
import {
  LayoutDashboard,
  Users,
  Briefcase,
  Sparkles,
  BookmarkCheck,
  Calendar,
  BarChart3,
  ScrollText,
  Settings,
  LogOut,
  Layers,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

export type NavPage =
  | 'dashboard'
  | 'candidates'
  | 'jobs'
  | 'screening'
  | 'shortlisted'
  | 'interviews'
  | 'analytics'
  | 'audit-logs'
  | 'settings';

interface SidebarProps {
  currentPage: NavPage;
  onNavigate: (page: NavPage) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  counts: {
    totalCandidates: number;
    shortlisted: number;
    interviews: number;
    jobs: number;
  };
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onNavigate,
  collapsed,
  onToggleCollapse,
  counts,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'candidates', label: 'Candidates', icon: Users, count: counts.totalCandidates },
    { id: 'jobs', label: 'Job Positions', icon: Briefcase, count: counts.jobs },
    { id: 'screening', label: 'AI Screener', icon: Sparkles, badge: 'Active' },
    { id: 'shortlisted', label: 'Shortlisted', icon: BookmarkCheck, count: counts.shortlisted },
    { id: 'interviews', label: 'Interviews', icon: Calendar, count: counts.interviews },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'audit-logs', label: 'Audit Logs', icon: ScrollText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside
      className={`bg-[#0f172a] text-slate-300 flex flex-col justify-between transition-all duration-200 border-r border-slate-800 z-30 shrink-0 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Top Header & Brand */}
      <div>
        <div className="h-16 px-4 flex items-center justify-between border-b border-slate-800/80">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shrink-0 shadow-sm">
              <Layers className="w-5 h-5" />
            </div>
            {!collapsed && (
              <div className="truncate">
                <span className="font-bold text-sm text-white tracking-tight block truncate">
                  Smart Resume
                </span>
                <span className="text-[10px] text-blue-400 font-semibold uppercase tracking-wider block">
                  Enterprise Screener
                </span>
              </div>
            )}
          </div>
          <button
            onClick={onToggleCollapse}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className="hidden md:flex p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id as NavPage)}
                title={collapsed ? item.label : undefined}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors group ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center space-x-3 truncate">
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'}`} />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </div>

                {!collapsed && (
                  <div>
                    {item.count !== undefined && item.count > 0 && (
                      <span
                        className={`text-[10px] font-mono px-1.5 py-0.5 rounded-full ${
                          isActive ? 'bg-blue-700 text-white' : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {item.count}
                      </span>
                    )}
                    {item.badge && (
                      <span className="text-[10px] font-semibold uppercase px-1.5 py-0.2 rounded bg-blue-500/20 text-blue-300 border border-blue-400/30">
                        {item.badge}
                      </span>
                    )}
                  </div>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* User Profile & Logout Bottom */}
      <div className="p-3 border-t border-slate-800/80">
        <div className={`flex items-center ${collapsed ? 'justify-center' : 'justify-between'} p-2 rounded-lg bg-slate-900/60 border border-slate-800`}>
          <div className="flex items-center space-x-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-slate-700 text-slate-200 font-bold text-xs flex items-center justify-center border border-slate-600 shrink-0">
              SJ
            </div>
            {!collapsed && (
              <div className="truncate">
                <p className="text-xs font-semibold text-white truncate">Sarah Jenkins</p>
                <p className="text-[11px] text-slate-400 truncate">Lead Talent Partner</p>
              </div>
            )}
          </div>
          {!collapsed && (
            <button
              title="Sign Out"
              aria-label="Sign Out"
              className="p-1.5 text-slate-400 hover:text-rose-400 rounded hover:bg-slate-800 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
};
