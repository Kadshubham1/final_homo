import React from 'react';
import { FiAlertTriangle, FiShieldOff, FiX } from 'react-icons/fi';

const SecurityAlertModal = ({ isOpen, onClose, message, type = 'harmful' }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border-4 border-red-500 animate-in zoom-in-95 duration-300">
        
        {/* Warning Header */}
        <div className="bg-red-500 p-8 flex flex-col items-center text-white relative">
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 p-2 hover:bg-black/10 rounded-full transition"
          >
            <FiX size={24} />
          </button>
          
          <div className="bg-white/20 p-4 rounded-full mb-4 animate-bounce">
            <FiAlertTriangle size={48} className="text-white" />
          </div>
          
          <h2 className="text-2xl font-black uppercase tracking-tighter">Security Threat Blocked</h2>
        </div>

        {/* Content */}
        <div className="p-8 text-center">
          <div className="text-red-600 font-black text-xl mb-4 italic">
            "this file is Harmfull"
          </div>
          
          <div className="bg-gray-50 border border-gray-100 rounded-xl p-4 mb-6 text-left">
            <p className="text-xs font-bold text-gray-400 uppercase mb-1">System Report:</p>
            <p className="text-sm text-gray-700 font-medium">
              {message || 'Suspicious patterns detected in upload payload. System self-protection engaged.'}
            </p>
          </div>

          <p className="text-sm text-gray-500 mb-8 px-4 leading-relaxed">
            Our homomorphic security layer identified this file as a potential threat to the system infrastructure. The upload has been terminated and logged for forensic review.
          </p>

          <button
            onClick={onClose}
            className="w-full py-4 bg-gray-900 text-white rounded-2xl font-bold text-lg hover:bg-red-600 transition-all shadow-xl hover:shadow-red-500/30 flex items-center justify-center gap-3 group"
          >
            <FiShieldOff className="group-hover:rotate-12 transition-transform" />
            Understood & Acknowledge
          </button>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 py-3 px-6 text-center border-t border-gray-100">
          <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
            🛡️ Unified Security Intelligence Subsystem
          </span>
        </div>
      </div>
    </div>
  );
};

export default SecurityAlertModal;
