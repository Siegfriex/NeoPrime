import React, { useState } from 'react';
import { STUDENTS } from '../services/mockData';
import { Link } from 'react-router-dom';
import { Search, Plus, ChevronDown, ChevronRight, School, Users as UsersIcon } from 'lucide-react';
import { Student } from '../types';

const StudentList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedUniv, setExpandedUniv] = useState<string | null>(null);

  const groupedStudents = STUDENTS.reduce((acc, student) => {
    const univ = student.targetUniversity;
    if (!acc[univ]) {
      acc[univ] = [];
    }
    acc[univ].push(student);
    return acc;
  }, {} as Record<string, Student[]>);

  const filteredGroups = Object.entries(groupedStudents).reduce((acc, [univ, students]) => {
    const filtered = students.filter(s => 
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.school.toLowerCase().includes(searchTerm.toLowerCase())
    );
    if (filtered.length > 0) {
      acc[univ] = filtered;
    }
    return acc;
  }, {} as Record<string, Student[]>);

  const toggleUniv = (univ: string) => {
    setExpandedUniv(expandedUniv === univ ? null : univ);
  };

  return (
    <div className="max-w-6xl mx-auto pb-12 animate-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center mb-8">
        <div>
           <h1 className="text-3xl font-bold text-gray-900 tracking-tight">학생 분석</h1>
           <p className="text-gray-500 mt-2">목표 대학별로 학생들을 관리하고 분석합니다.</p>
        </div>
        <button className="flex items-center px-6 py-3 bg-[#FC6401] text-white rounded-xl hover:bg-[#e55a00] transition-all shadow-lg shadow-[#FC6401]/30 font-semibold transform hover:-translate-y-0.5">
            <Plus className="w-5 h-5 mr-2" />
            학생 추가
        </button>
      </div>

      <div className="mb-8 relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          className="block w-full pl-11 pr-4 py-4 bg-white border border-gray-200 rounded-2xl leading-5 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#FC6401] focus:border-[#FC6401] sm:text-sm shadow-sm transition-all hover:shadow-md"
          placeholder="학생 이름 또는 학교명 검색..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="space-y-4">
        {Object.keys(filteredGroups).length === 0 ? (
           <div className="text-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm">
             <div className="bg-gray-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
               <UsersIcon className="w-10 h-10 text-gray-300" />
             </div>
             <p className="text-gray-500 text-lg">검색 조건에 맞는 학생이 없습니다.</p>
           </div>
        ) : (
          Object.entries(filteredGroups).map(([univ, students]) => {
            const isExpanded = expandedUniv === univ;
            return (
              <div key={univ} className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200">
                <button 
                  onClick={() => toggleUniv(univ)}
                  className="w-full flex items-center justify-between p-6 bg-white hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-5">
                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-colors ${isExpanded ? 'bg-[#FFF0E6] text-[#FC6401]' : 'bg-gray-100 text-gray-500'}`}>
                      <School className="w-7 h-7" />
                    </div>
                    <div className="text-left">
                      <h3 className="text-xl font-bold text-gray-900">{univ}</h3>
                      <p className="text-sm text-gray-500 mt-0.5">{students.length}명 준비 중</p>
                    </div>
                  </div>
                  <ChevronDown className={`w-6 h-6 text-gray-400 transition-transform duration-300 ${isExpanded ? 'transform rotate-180 text-[#FC6401]' : ''}`} />
                </button>

                {isExpanded && (
                  <div className="border-t border-gray-100 bg-[#F7F9FB] p-4 animate-in slide-in-from-top-2 duration-200">
                    <div className="grid gap-3">
                      {students.map(student => (
                        <Link 
                          key={student.id} 
                          to={`/students/${student.id}`}
                          className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200 hover:border-[#FC6401] hover:shadow-lg hover:shadow-[#FC6401]/5 transition-all group"
                        >
                          <div className="flex items-center gap-5">
                            <img src={student.avatarUrl} alt={student.name} className="w-14 h-14 rounded-full object-cover border-4 border-[#F7F9FB] shadow-sm group-hover:scale-105 transition-transform" />
                            <div>
                              <div className="flex items-center gap-3">
                                <span className="font-bold text-lg text-gray-900 group-hover:text-[#FC6401] transition-colors">{student.name}</span>
                                <span className={`px-2.5 py-1 rounded-md text-[11px] font-bold uppercase tracking-wide
                                  ${student.currentLevel.startsWith('A') ? 'bg-[#FFF0E6] text-[#FC6401]' : 
                                    student.currentLevel.startsWith('B') ? 'bg-emerald-50 text-emerald-600' : 'bg-gray-100 text-gray-600'}`}>
                                  Level {student.currentLevel}
                                </span>
                              </div>
                              <div className="text-sm text-gray-500 flex gap-2 mt-1">
                                <span className="font-medium">{student.grade}</span>
                                <span className="text-gray-300">•</span>
                                <span>{student.school}</span>
                                <span className="text-gray-300">•</span>
                                <span>{student.major}</span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-8">
                             <div className="hidden md:flex flex-col items-end mr-4">
                                <span className="text-[10px] text-gray-400 uppercase font-bold tracking-wider mb-1">국어 표점</span>
                                <span className="font-mono font-bold text-gray-800 bg-gray-50 px-2 py-1 rounded-md">{student.academicScores?.korean.standardScore || '-'}</span>
                             </div>
                             <div className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center group-hover:bg-[#FC6401] transition-colors">
                                <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
                             </div>
                          </div>
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default StudentList;