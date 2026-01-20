import React from 'react';
import { STUDENTS } from '../services/mockData';
import { Users, TrendingUp, Award, AlertCircle, FileEdit, ArrowUpRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const totalStudents = STUDENTS.length;
  const avgLevel = "B+"; 
  const predictedPass = 42;

  // Level Distribution Data
  const levelData = [
    { name: 'A+', count: STUDENTS.filter(s => s.currentLevel === 'A+').length },
    { name: 'A', count: STUDENTS.filter(s => s.currentLevel === 'A').length },
    { name: 'B+', count: STUDENTS.filter(s => s.currentLevel === 'B+').length },
    { name: 'B', count: STUDENTS.filter(s => s.currentLevel === 'B').length },
    { name: 'C', count: STUDENTS.filter(s => s.currentLevel === 'C').length },
  ];
  
  // New Color Palette using shades of Orange #FC6401
  const COLORS = ['#FC6401', '#FD8334', '#FEA267', '#FFC199', '#E5E7EB'];

  const StatCard = ({ title, value, sub, icon: Icon }: any) => (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow group">
      <div className="flex justify-between items-start mb-4">
        <div className="p-3 rounded-xl bg-[#FFF0E6] text-[#FC6401] group-hover:bg-[#FC6401] group-hover:text-white transition-colors">
          <Icon className="w-6 h-6" />
        </div>
        <button className="text-gray-300 hover:text-gray-500">•••</button>
      </div>
      <div>
        <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
        <h3 className="text-3xl font-bold text-gray-900 mb-2">{value}</h3>
        <div className="flex items-center gap-1 text-xs font-medium">
             <span className="flex items-center text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                <ArrowUpRight className="w-3 h-3 mr-0.5" />
                {sub.split(' ')[0]}
             </span>
             <span className="text-gray-400 ml-1">{sub.split(' ').slice(1).join(' ')}</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
            <h1 className="text-2xl font-bold text-gray-900">Academy Overview</h1>
            <p className="text-gray-500 mt-1">Welcome back, here is what's happening today.</p>
        </div>
        <div className="flex gap-3">
             <button className="px-4 py-2 bg-white border border-gray-200 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-50 transition-colors">
                Export Report
             </button>
             <button className="px-4 py-2 bg-[#FC6401] text-white rounded-xl text-sm font-medium hover:bg-[#e55a00] shadow-lg shadow-[#FC6401]/30 transition-all">
                Explore Insights
             </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Total Students" 
          value={totalStudents} 
          sub="+7% from last month" 
          icon={Users} 
        />
        <StatCard 
          title="Avg. Level" 
          value={avgLevel} 
          sub="+12% vs last year" 
          icon={TrendingUp} 
        />
        <StatCard 
          title="Predicted Pass" 
          value={predictedPass} 
          sub="+4% Seoul Metro Area" 
          icon={Award} 
        />
        <StatCard 
          title="Evaluations" 
          value="5" 
          sub="Pending this week" 
          icon={AlertCircle} 
        />
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Col - Charts */}
        <div className="lg:col-span-2 space-y-8">
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex justify-between items-center mb-8">
                 <h3 className="text-lg font-bold text-gray-900">Student Level Distribution</h3>
                 <div className="flex gap-2">
                    <span className="w-3 h-3 rounded-full bg-[#FC6401]"></span>
                    <span className="text-xs text-gray-500">Current Semester</span>
                 </div>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={levelData} barSize={40}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} />
                  <Tooltip 
                    cursor={{fill: '#F7F9FB'}}
                    contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'}}
                  />
                  <Bar dataKey="count" radius={[8, 8, 8, 8]}>
                    {levelData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
             <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-bold text-gray-900">Admission Predictions</h3>
                <Link to="/analytics" className="text-sm text-[#FC6401] font-medium hover:text-[#e55a00]">View Full Analysis &rarr;</Link>
             </div>
             <div className="space-y-6">
                {['Hongik Univ.', 'Seoul Nat\'l Univ.', 'Ewha Womans Univ.'].map((univ, idx) => (
                    <div key={univ} className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="font-semibold text-gray-700">{univ}</span>
                            <span className="text-gray-900 font-bold">{85 - idx * 12}%</span>
                        </div>
                        <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
                            <div 
                                className="h-full rounded-full transition-all duration-1000 ease-out" 
                                style={{
                                    width: `${85 - idx * 12}%`,
                                    backgroundColor: idx === 0 ? '#FC6401' : idx === 1 ? '#FD8334' : '#FEA267'
                                }}
                            ></div>
                        </div>
                    </div>
                ))}
             </div>
          </div>
        </div>

        {/* Right Col - Quick Actions & Notifications */}
        <div className="space-y-8">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
                <div className="space-y-3">
                    <Link to="/evaluations/new" className="flex items-center p-4 rounded-xl border border-gray-100 hover:border-[#FC6401] hover:bg-[#FFF0E6] transition-all group">
                        <div className="bg-gray-100 p-2.5 rounded-lg group-hover:bg-[#FC6401] transition-colors">
                            <FileEdit className="w-5 h-5 text-gray-600 group-hover:text-white" />
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-bold text-gray-900 group-hover:text-[#FC6401]">New Evaluation</p>
                            <p className="text-xs text-gray-500">Log weekly progress</p>
                        </div>
                    </Link>
                     <Link to="/students" className="flex items-center p-4 rounded-xl border border-gray-100 hover:border-[#FC6401] hover:bg-[#FFF0E6] transition-all group">
                        <div className="bg-gray-100 p-2.5 rounded-lg group-hover:bg-[#FC6401] transition-colors">
                            <Users className="w-5 h-5 text-gray-600 group-hover:text-white" />
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-bold text-gray-900 group-hover:text-[#FC6401]">Add Student</p>
                            <p className="text-xs text-gray-500">Register new enrollee</p>
                        </div>
                    </Link>
                </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                 <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-900">Notifications</h3>
                    <button className="text-xs text-gray-400 hover:text-gray-600">Mark all read</button>
                 </div>
                 <div className="space-y-0">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="flex gap-4 items-start p-3 hover:bg-gray-50 rounded-xl transition-colors cursor-pointer">
                             <div className="w-2 h-2 rounded-full bg-[#FC6401] mt-2 flex-shrink-0 shadow-[0_0_8px_rgba(252,100,1,0.5)]"></div>
                             <div>
                                 <p className="text-sm text-gray-800 font-medium">Weekly report for <span className="font-bold text-gray-900">Ji-min Kim</span> is ready.</p>
                                 <p className="text-xs text-gray-400 mt-1">2 hours ago</p>
                             </div>
                        </div>
                    ))}
                 </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;