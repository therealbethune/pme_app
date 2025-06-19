import React from 'react';
import { motion } from 'framer-motion';
import { 
  Upload as UploadIcon, 
  FileText, 
  TrendingUp, 
  Shield, 
  CheckCircle,
  ArrowRight,
  Database,
  Clock
} from 'lucide-react';

const Upload: React.FC = () => {
  const features = [
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Bank-grade encryption and compliance standards'
    },
    {
      icon: TrendingUp,
      title: 'Advanced Analytics',
      description: 'Institutional-quality performance metrics'
    },
    {
      icon: Clock,
      title: 'Real-time Processing',
      description: 'Instant analysis and reporting capabilities'
    }
  ];

  const fileFormats = [
    { name: 'Excel Files', ext: '.xlsx, .xls', icon: FileText },
    { name: 'CSV Files', ext: '.csv', icon: Database },
    { name: 'Text Files', ext: '.txt, .tsv', icon: FileText }
  ];

  return (
    <div className="min-h-full bg-white">
      {/* Header Section */}
      <section className="section-sm bg-gradient-to-br from-primary-50 via-white to-accent">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-display text-gray-900 mb-6">
              Upload Your Fund Data
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Securely upload your portfolio data to generate comprehensive PME analysis 
              and institutional-grade performance metrics.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            {/* Upload Form */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="space-y-8"
            >
              {/* Main Upload Area */}
              <div className="card p-8">
                <div className="text-center">
                  <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <UploadIcon className="w-8 h-8 text-primary-600" />
                  </div>
                  <h3 className="text-title text-gray-900 mb-4">
                    Drop files to upload
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Drag and drop your fund data files here, or click to browse
                  </p>
                  
                  <div className="border-2 border-dashed border-primary-200 rounded-xl p-12 hover:border-primary-300 transition-colors cursor-pointer group">
                    <div className="text-center">
                      <UploadIcon className="w-12 h-12 text-primary-400 mx-auto mb-4 group-hover:scale-110 transition-transform" />
                      <p className="text-lg font-medium text-gray-700 mb-2">
                        Choose files or drag them here
                      </p>
                      <p className="text-sm text-gray-500">
                        Maximum file size: 50MB
                      </p>
                    </div>
                  </div>

                  <button className="btn-primary mt-6 w-full group">
                    <UploadIcon className="w-5 h-5 mr-2" />
                    Select Files
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </div>

              {/* Supported Formats */}
              <div className="card p-6">
                <h4 className="font-semibold text-gray-900 mb-4">Supported File Formats</h4>
                <div className="space-y-3">
                  {fileFormats.map((format, index) => (
                    <div key={index} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                      <format.icon className="w-5 h-5 text-gray-500" />
                      <div>
                        <p className="font-medium text-gray-900">{format.name}</p>
                        <p className="text-sm text-gray-500">{format.ext}</p>
                      </div>
                      <CheckCircle className="w-5 h-5 text-green-500 ml-auto" />
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>

            {/* Features & Benefits */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="space-y-8"
            >
              <div>
                <h3 className="text-title text-gray-900 mb-6">
                  Why Choose Our Platform?
                </h3>
                <div className="space-y-6">
                  {features.map((feature, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
                      className="flex items-start space-x-4 p-4 rounded-xl hover:bg-gray-50 transition-colors"
                    >
                      <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
                        <feature.icon className="w-6 h-6 text-primary-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">
                          {feature.title}
                        </h4>
                        <p className="text-gray-600">
                          {feature.description}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Data Requirements */}
              <div className="card p-6">
                <h4 className="font-semibold text-gray-900 mb-4">Data Requirements</h4>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                    <span className="text-gray-700">Date column (MM/DD/YYYY format)</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                    <span className="text-gray-700">Cash flow amounts (negative for outflows)</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                    <span className="text-gray-700">Fund/Investment identifiers</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                    <span className="text-gray-700">Market values (optional)</span>
                  </div>
                </div>
              </div>

              {/* Security Notice */}
              <div className="bg-primary-50 border border-primary-200 rounded-xl p-6">
                <div className="flex items-start space-x-3">
                  <Shield className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="font-semibold text-primary-900 mb-2">
                      Enterprise-Grade Security
                    </h4>
                    <p className="text-primary-800 text-sm">
                      Your data is encrypted during transmission and storage. 
                      We comply with SOC 2 Type II and maintain strict data governance protocols.
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Upload; 