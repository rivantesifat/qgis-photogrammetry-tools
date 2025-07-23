# QGIS Photogrammetry Tools Plugin

A comprehensive QGIS plugin designed for photogrammetry workflows, providing essential tools for production management, spatial analysis, and quality control processes.

![QGIS Version](https://img.shields.io/badge/QGIS-3.x-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)
![Project Screenshot](Demo.JPG)

## Overview

This plugin streamlines photogrammetry workflows by providing a comprehensive toolset in a convenient dock widget. It handles coordinate reference systems automatically, ensures precise measurements, and includes specialized tools for production status tracking and quality control.

## Key Features

### 🎯 Production Management System
- **Production Status Updater**: Color-coded buttons for marking features as Done/Not Done
- **QC Status Updater**: Quality control workflow with Done and Smart Geofill options
- **Smart Status Tracking**: Automated remarks and status updates for selected features

### 🛠️ Spatial Analysis Tools
- **Precision Grid Creation**: Generate measurement grids with custom spacing and automatic CRS alignment
- **Advanced Buffer Tool**: Create buffers with 50 segments for smooth edges and precise measurements
- **Vector Layer Creation**: Create new Point and Polygon layers with proper CRS handling
- **Geometry Conversion**: Convert polygons to lines and generate line intersection points

### 📊 Data Management
- **Field Management**: Add standardized bridge and seamline fields including new "Rework" field
- **Export Tools**: Save selected features to new shapefiles with proper encoding
- **CRS Validation**: Automatic coordinate reference system validation for metric units

### 🎨 User Interface
- **Collapsible Tool Groups**: Organized interface with checkable group boxes
- **Global CRS Selector**: Centralized coordinate system management
- **Color-coded Buttons**: Visual status indicators for production workflow
- **Scrollable Interface**: Compact design that fits in QGIS dock areas

## Supported Coordinate Systems

The plugin is optimized for metric coordinate reference systems:

- **EPSG:28992** - RD New (Netherlands)
- **EPSG:31370** - Belgian Lambert 72 (Belgium)
- **EPSG:2154** - RGF93 / Lambert-93 (France)
- **EPSG:32631** - WGS 84 / UTM zone 31N

## Installation

### Method 1: Manual Installation
1. Download the plugin files
2. Copy to your QGIS plugins directory:
   - **Windows**: `C:\Users\[username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\photogrammetry_tools\`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/photogrammetry_tools/`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/photogrammetry_tools/`
3. Restart QGIS
4. Enable the plugin: **Plugins → Manage and Install Plugins → Installed → Photogrammetry Tools**

### Method 2: Development Setup
```bash
# Clone the repository
git clone https://github.com/rivantesifat/qgis-photogrammetry-tools.git

# Create symbolic link to QGIS plugins directory
# Linux/macOS:
ln -s /path/to/qgis-photogrammetry-tools ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/photogrammetry_tools

# Windows (run as administrator):
mklink /D "C:\Users\[username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\photogrammetry_tools" "C:\path\to\qgis-photogrammetry-tools"
```

## Quick Start Guide

### 1. Setup Your Workspace
1. Open the plugin dock: **Plugins → Photogrammetry Tools**
2. Select your working CRS from the dropdown
3. Enable the tool groups you need by checking the group boxes

### 2. Production Status Management
```
Select features → Choose status button → Features updated automatically
```
- **Green "Done"**: Mark completed features
- **Red "Not Done"**: Mark pending features  
- **Blue "No Need to Work"**: Mark features requiring no work
- **Orange "Smart Geofill"**: Mark features for automated processing

### 3. Create Precision Grids
1. Select a reference layer to define the grid extent
2. Enter grid size in meters (e.g., 1000 for 1km × 1km cells)
3. Click "Create Grid"
4. Grid is automatically aligned and saved as shapefile

### 4. Generate Smooth Buffers
1. Select a polygon layer
2. Enter buffer distance in meters (e.g., 250)
3. Click "Create Buffer"
4. Buffer created with 50 segments for smooth curves

## Field Standards

### Bridge Fields (Add Bridge Fields button)
| Field | Type | Description |
|-------|------|-------------|
| Part | Integer | Part number identifier |
| Assign | String | Assignment information |
| Status | String | Production status |
| Remarks | String | Production remarks |
| QC | String | Quality control status |
| QCRemarks | String | QC remarks |
| Rework | String | Rework requirements |

### Seamline Fields (Add Seamline Fields button)
Includes all Bridge fields plus:
| Field | Type | Description |
|-------|------|-------------|
| Geo_Assign | String | Geometry assignment |
| Geo_Stat | String | Geometry status |
| Geo_QC | String | Geometry QC status |

## Technical Requirements

### Dependencies
- **QGIS**: 3.0 or higher
- **PyQt**: 5.x (included with QGIS)
- **QGIS Processing**: Framework (included with QGIS)

### Hardware Requirements
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 50MB for plugin installation
- **Display**: 1024x768 minimum resolution

## Advanced Features

### CRS Handling
- Automatic validation ensures selected CRS uses meters
- Automatic reprojection when layers use different CRS
- Project CRS automatically updated for consistent measurements
- Transform context handling for accurate coordinate transformations

### Processing Algorithms
- **Grid Creation**: Uses `native:creategrid` with precise alignment
- **Buffer Creation**: Uses `native:buffer` with 50 segments and round joins
- **Line Intersections**: Uses `native:lineintersections` for point generation
- **Polygon to Lines**: Uses `native:polygonstolines` for conversion

### Error Handling
- Input validation for numeric fields
- CRS compatibility checking
- Layer type validation
- Feature selection verification
- File path validation for exports

## Troubleshooting

### Common Issues

**Grid not aligned properly**
- Ensure reference layer has features
- Check that grid size is appropriate for layer extent
- Verify CRS uses meters as units

**Buffer appears jagged**
- Plugin creates buffers with 50 segments for smooth curves
- Older QGIS versions may have different defaults
- Check that input layer is valid polygon geometry

**Fields not added**
- Layer must be editable
- Check that field names don't already exist
- Ensure layer is a vector layer, not raster

**Status updates not working**
- Select features before clicking status buttons
- Ensure required fields exist (use Add Bridge/Seamline Fields first)
- Check that layer is in edit mode

## Contributing

We welcome contributions! Here's how to help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add some amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Test with multiple CRS systems
- Ensure backward compatibility with QGIS 3.0+

## Changelog

### Version 1.0.0 (Current)
- ✅ Initial release with full feature set
- ✅ Production status management with color-coded buttons
- ✅ QC workflow integration
- ✅ Precision grid creation with automatic alignment
- ✅ Advanced buffer tool with smooth edges (50 segments)
- ✅ Field management for bridge and seamline workflows
- ✅ Export functionality with proper encoding
- ✅ Added "Rework" field to standard field sets
- ✅ Comprehensive CRS handling and validation
- ✅ Scrollable dock interface with collapsible groups

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/rivantesifat/qgis-photogrammetry-tools/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/rivantesifat/qgis-photogrammetry-tools/issues)
- 📧 **Email**: nashidsifat@outlook.com

## Acknowledgments

- **QGIS Development Team** for the excellent framework and processing algorithms
- **PyQt Team** for the robust UI framework
- **Contributors** and beta testers who helped refine this plugin
- **Photogrammetry Community** for workflow insights and requirements

---

**Made with ❤️ for the QGIS and Photogrammetry Community**
