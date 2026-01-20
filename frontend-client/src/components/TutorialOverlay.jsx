import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiArrowRight, FiInfo } from 'react-icons/fi';

const TutorialOverlay = ({ isOpen, onClose, steps = [] }) => {
  const [currentStep, setCurrentStep] = useState(0);

  // If no steps provided, don't render
  if (!steps.length) return null;

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
        setCurrentStep(prev => prev + 1);
    } else {
        onClose();
    }
  };

  const handleSkip = () => {
      onClose();
  };

  const currentStepData = steps[currentStep];

  return createPortal(
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[9999] pointer-events-none">
          {/* Dark Overlay with "Hole" logic would be complex, doing simple highlights for now */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm pointer-events-auto"
            onClick={handleSkip} // Click outside to close/skip
          />

          {/* Central Tutorial Card */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <motion.div 
               initial={{ scale: 0.9, opacity: 0 }}
               animate={{ scale: 1, opacity: 1 }}
               exit={{ scale: 0.9, opacity: 0 }}
               className="pointer-events-auto bg-dark-850 border border-ohm-cyan/30 p-6 rounded-2xl shadow-neon w-full max-w-md mx-4 relative"
               onClick={(e) => e.stopPropagation()}
            >
                <div className="absolute -top-10 left-1/2 transform -translate-x-1/2">
                    <div className="w-20 h-20 bg-dark-900 rounded-full border-4 border-dark-950 flex items-center justify-center shadow-lg">
                        <div className="text-4xl">💡</div>
                    </div>
                </div>

               <div className="mt-8 text-center">
                   <h3 className="text-xl font-bold text-white mb-2">{currentStepData.title}</h3>
                   <p className="text-gray-400 text-sm mb-6 leading-relaxed">
                       {currentStepData.content}
                   </p>
                   
                   {/* Progress Indicators */}
                   <div className="flex justify-center gap-2 mb-6">
                       {steps.map((_, idx) => (
                           <div 
                             key={idx} 
                             className={`h-1.5 rounded-full transition-all duration-300 ${idx === currentStep ? 'w-8 bg-ohm-cyan' : 'w-2 bg-gray-700'}`}
                           />
                       ))}
                   </div>
               </div>

               <div className="flex justify-between items-center">
                   <button 
                     onClick={handleSkip}
                     className="text-gray-500 hover:text-white text-sm font-medium transition-colors"
                   >
                     Passer
                   </button>
                   <button 
                     onClick={handleNext}
                     className="bg-ohm-cyan hover:bg-ohm-cyan/80 text-dark-950 px-6 py-2 rounded-lg font-bold text-sm transition-colors flex items-center gap-2"
                   >
                     {currentStep === steps.length - 1 ? 'Terminer' : 'Suivant'}
                     <FiArrowRight />
                   </button>
               </div>
            </motion.div>
          </div>
        </div>
      )}
    </AnimatePresence>,
    document.body
  );
};

export default TutorialOverlay;
