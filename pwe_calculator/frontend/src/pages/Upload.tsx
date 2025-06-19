import React from 'react';
import { motion } from 'framer-motion';
import { IntelligentDataUpload } from '../components/IntelligentDataUpload';

const Upload: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="p-6 max-w-4xl mx-auto"
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Upload Fund Data
        </h1>
        <p className="text-gray-600">
          Upload your private equity fund data to begin PME analysis
        </p>
      </div>
      
      <IntelligentDataUpload />
    </motion.div>
  );
};

export default Upload; 