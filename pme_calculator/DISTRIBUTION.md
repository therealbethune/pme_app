# PME Calculator - Distribution Guide

## 🚀 **PyInstaller Distribution System**

The PME Calculator now includes a fully automated build system that creates standalone executables for easy distribution. Users can run the application without installing Python, Node.js, or any dependencies.

## 📦 **What Gets Built**

### **Single Executable Distribution**
- **macOS**: `PME Calculator.app` - Native app bundle
- **Windows**: `PME_Calculator.exe` - Standalone executable  
- **Linux**: `PME_Calculator` - Standalone binary

### **No Dependencies Required**
- ✅ No Python installation needed
- ✅ No Node.js or npm required
- ✅ No package installations
- ✅ All libraries bundled internally
- ✅ React frontend embedded

## 🛠️ **Building the Distribution**

### **Quick Build (Automated)**
```bash
# From the pme_calculator directory
python3 build.py
```

The automated build script will:
1. ✅ Check all dependencies
2. ✅ Build the React frontend
3. ✅ Package with PyInstaller  
4. ✅ Create distribution files
5. ✅ Generate installation instructions

### **Manual Build Process**

If you prefer manual control:

```bash
# 1. Build React frontend
cd frontend
npm run build
cd ..

# 2. Build with PyInstaller
cd backend
python3 -m PyInstaller --clean pme_calculator.spec
cd ..

# 3. Copy to distribution directory
mkdir -p dist
cp -r "backend/dist/PME Calculator.app" "dist/"
```

## 📋 **Build Requirements**

### **Development Machine**
- **Python 3.8+** with packages:
  - `pyinstaller`
  - `pandas`, `numpy`, `matplotlib`
  - `pywebview`, `openpyxl`, `xlrd`
- **Node.js 16+** with npm
- **Operating System**: macOS, Windows, or Linux

### **Target Machine** 
- **No requirements** - runs standalone!

## 📁 **Distribution Structure**

After building, you'll find in `dist/`:

```
dist/
├── PME Calculator.app          # macOS app bundle
├── README.md                   # Documentation  
└── INSTALLATION.txt           # Quick start guide
```

## 🎯 **Distribution Benefits**

### **For Users**
- **Zero Installation**: Just double-click to run
- **Professional Experience**: Native app behavior
- **No Technical Setup**: Works out of the box
- **Cross-Platform**: Same interface on all systems

### **For Developers**
- **Easy Distribution**: Single file to share
- **Version Control**: Consistent builds
- **No Support Issues**: Self-contained deployment
- **Professional Delivery**: App store-ready format

## 🔧 **Advanced Build Configuration**

### **Customizing the Build**

Edit `backend/pme_calculator.spec` to customize:

```python
# App bundle name and metadata
name='PME Calculator.app',
bundle_identifier='com.pme.calculator',
info_plist={
    'CFBundleName': 'PME Calculator',
    'CFBundleVersion': '1.0.0',
    # Add more customizations...
}

# Add custom icon
icon='path/to/icon.icns',  # macOS
icon='path/to/icon.ico',   # Windows
```

### **Build Optimization**

For smaller file sizes:
```python
# In pme_calculator.spec
excludes=[
    'test', 'tests', 'testing',
    'unittest', 'doctest', 'pdb',
    # Add more modules to exclude...
],
upx=True,  # Enable UPX compression
```

### **Debug Builds**

For troubleshooting:
```python
# In pme_calculator.spec
console=True,   # Show console window
debug=True,     # Enable debug output
```

## 🚀 **Deployment Scenarios**

### **Internal Distribution**
```bash
# Build and zip for internal sharing
python3 build.py
cd dist
zip -r "PME_Calculator_v1.0.zip" .
```

### **Professional Distribution**
```bash
# Build with code signing (macOS)
# Edit pme_calculator.spec:
codesign_identity="Developer ID Application: Your Name",

# Then build
python3 build.py
```

### **Enterprise Deployment**
- Place executable on network share
- Create installer package with scripts
- Use group policy for automatic deployment

## 📊 **Build Performance**

### **Typical Build Sizes**
- **macOS**: ~150-200 MB (app bundle)
- **Windows**: ~120-150 MB (executable)  
- **Linux**: ~100-130 MB (binary)

### **Build Times**
- **Frontend Build**: ~30-60 seconds
- **PyInstaller**: ~2-5 minutes
- **Total**: ~3-6 minutes

### **Runtime Performance**
- **Startup**: ~3-5 seconds (first launch)
- **Subsequent**: ~1-2 seconds
- **Memory**: ~150-250 MB typical usage
- **Performance**: Near-native speed

## 🔍 **Troubleshooting**

### **Common Build Issues**

**Missing Dependencies**:
```bash
pip3 install pyinstaller pandas numpy matplotlib pywebview openpyxl xlrd
```

**Frontend Build Fails**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**PyInstaller Errors**:
```bash
# Clear PyInstaller cache
python3 -m PyInstaller --clean --noconfirm backend/pme_calculator.spec
```

### **Runtime Issues**

**App Won't Launch**:
- Check file permissions (`chmod +x` on Linux)
- Run from terminal to see error messages
- Verify all data files are included

**Missing Features**:
- Ensure frontend `dist/` directory exists
- Check that `pme_app/` directory is included
- Verify PyInstaller spec includes all data files

## 🎉 **Success Validation**

### **Testing the Build**
1. ✅ Launch the executable
2. ✅ Upload a test CSV file  
3. ✅ Verify calculations work
4. ✅ Check charts display correctly
5. ✅ Test error handling

### **Distribution Checklist**
- [ ] Build completes without errors
- [ ] Executable launches successfully  
- [ ] All features function correctly
- [ ] File uploads work properly
- [ ] Charts render accurately
- [ ] Error messages display appropriately
- [ ] README and instructions included

## 🌟 **Next Steps**

After successful distribution setup:

1. **🔒 Code Signing**: Add digital signatures for security
2. **📦 Installer Creation**: Build MSI/PKG/DEB packages
3. **🔄 Auto-Updates**: Implement update mechanisms
4. **📊 Analytics**: Add usage tracking
5. **🎨 Branding**: Custom icons and splash screens

---

**The PME Calculator is now ready for professional distribution!** 🎉

Users can simply double-click the executable to access the full power of your PME analysis tools without any technical setup. 