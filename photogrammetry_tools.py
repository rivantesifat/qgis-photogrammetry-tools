import os
import math
from qgis.PyQt.QtWidgets import (QDockWidget, QPushButton, QVBoxLayout, QWidget,
                                 QFileDialog, QMessageBox, QHBoxLayout, QLabel,
                                 QAction, QFrame, QComboBox, QLineEdit,
                                 QGroupBox, QInputDialog)
from qgis.PyQt import QtGui
from qgis.PyQt.QtCore import Qt
from qgis.core import (QgsVectorLayer, QgsProject, QgsRectangle, QgsFeature,
                       QgsGeometry, QgsVectorFileWriter, QgsFields, QgsField,
                       QgsCoordinateReferenceSystem, QgsWkbTypes, QgsPointXY,
                       QgsCoordinateTransform, QgsUnitTypes)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant
import processing


class PhotogrammetryToolsDock(QDockWidget):
    def __init__(self, iface):
        super().__init__("Photogrammetry Tools")
        self.iface = iface
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("PhotogrammetryToolsDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Main widget with scroll area
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        # Create scroll area
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.main_layout.addWidget(scroll_widget)

        # Make main widget scrollable
        self.setWidget(self.main_widget)

        # ========================
        # Global CRS Selector
        # ========================
        crs_layout = QHBoxLayout()
        crs_layout.addWidget(QLabel("Working CRS:"))
        self.global_crs_combo = QComboBox()
        self.global_crs_combo.addItems(["EPSG:28992", "EPSG:31370", "EPSG:2154", "EPSG:32631"])
        crs_layout.addWidget(self.global_crs_combo)
        self.scroll_layout.addLayout(crs_layout)

        # ========================
        # PRODUCTION STATUS UPDATER
        # ========================
        production_group = QGroupBox("Production Status Updater")
        production_group.setCheckable(True)
        production_group.setChecked(False)
        prod_layout = QHBoxLayout()

        self.btn_done = QPushButton("Done")
        self.btn_done.setStyleSheet("background-color: #7cc47f;")
        self.btn_done.clicked.connect(lambda: self.set_production_status('Done'))

        self.btn_not_done = QPushButton("Not Done")
        self.btn_not_done.setStyleSheet("background-color: #e8a8a8;")
        self.btn_not_done.clicked.connect(lambda: self.set_production_status('Not Done'))

        self.btn_no_need = QPushButton("No Need to Work")
        self.btn_no_need.setStyleSheet("background-color: #a8c4e8;")
        self.btn_no_need.clicked.connect(lambda: self.set_production_remarks('No Need to Work'))

        self.btn_smart_geofill = QPushButton("Smart Geofill")
        self.btn_smart_geofill.setStyleSheet("background-color: #e8d4a8;")
        self.btn_smart_geofill.clicked.connect(lambda: self.set_production_remarks('Smart Geofill'))

        prod_layout.addWidget(self.btn_done)
        prod_layout.addWidget(self.btn_not_done)
        prod_layout.addWidget(self.btn_no_need)
        prod_layout.addWidget(self.btn_smart_geofill)
        production_group.setLayout(prod_layout)
        self.scroll_layout.addWidget(production_group)

        # ========================
        # QC STATUS UPDATER
        # ========================
        qc_group = QGroupBox("QC Status Updater")
        qc_group.setCheckable(True)
        qc_group.setChecked(False)
        qc_layout = QHBoxLayout()

        self.btn_qc_done = QPushButton("Done")
        self.btn_qc_done.setStyleSheet("background-color: #4CAF50; font-weight: bold;")
        self.btn_qc_done.clicked.connect(lambda: self.set_qc_status('Done'))

        self.btn_qc_smart_geofill = QPushButton("Smart Geofill")
        self.btn_qc_smart_geofill.setStyleSheet("background-color: #FFC107; font-weight: bold;")
        self.btn_qc_smart_geofill.clicked.connect(lambda: self.set_qc_remarks('Smart Geofill'))

        qc_layout.addWidget(self.btn_qc_done)
        qc_layout.addWidget(self.btn_qc_smart_geofill)
        qc_group.setLayout(qc_layout)
        self.scroll_layout.addWidget(qc_group)

        # Add separator between status updaters and tools
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.scroll_layout.addWidget(separator)

        # ========================
        # Grid Creation Tool
        # ========================
        grid_group = QGroupBox("Grid Creation")
        grid_group.setCheckable(True)
        grid_group.setChecked(False)
        grid_layout = QHBoxLayout()

        self.grid_size_input = QLineEdit("1000")
        self.grid_size_input.setValidator(QtGui.QDoubleValidator(1, 100000, 2))

        self.btn_grid = QPushButton("Create Grid")
        self.btn_grid.setIcon(QIcon(":/images/themes/default/grid.svg"))
        self.btn_grid.clicked.connect(self.create_grid)

        grid_layout.addWidget(QLabel("Size (m):"))
        grid_layout.addWidget(self.grid_size_input)
        grid_layout.addWidget(self.btn_grid)
        grid_group.setLayout(grid_layout)
        self.scroll_layout.addWidget(grid_group)

        # ========================
        # Buffer Tool
        # ========================
        buffer_group = QGroupBox("Buffer Tool")
        buffer_group.setCheckable(True)
        buffer_group.setChecked(False)
        buffer_layout = QHBoxLayout()

        self.buffer_size_input = QLineEdit("250")
        self.buffer_size_input.setValidator(QtGui.QDoubleValidator(1, 100000, 2))

        self.btn_buffer = QPushButton("Create Buffer")
        self.btn_buffer.setIcon(QIcon(":/images/themes/default/buffer.svg"))
        self.btn_buffer.clicked.connect(self.create_buffer)

        buffer_layout.addWidget(QLabel("Distance (m):"))
        buffer_layout.addWidget(self.buffer_size_input)
        buffer_layout.addWidget(self.btn_buffer)
        buffer_group.setLayout(buffer_layout)
        self.scroll_layout.addWidget(buffer_group)

        # ========================
        # Vector Creation Tool
        # ========================
        vector_group = QGroupBox("Vector Creation Tool")
        vector_group.setCheckable(True)
        vector_group.setChecked(False)
        vector_layout = QVBoxLayout()

        # Geometry Type Selection
        geom_layout = QHBoxLayout()
        geom_layout.addWidget(QLabel("Geometry Type:"))
        self.geom_combo = QComboBox()
        self.geom_combo.addItems(["Point", "Polygon"])
        geom_layout.addWidget(self.geom_combo)
        vector_layout.addLayout(geom_layout)

        # Vector Creation Button
        self.btn_create_vector = QPushButton("Create Vector Layer")
        self.btn_create_vector.clicked.connect(self.create_vector_layer)
        vector_layout.addWidget(self.btn_create_vector)

        vector_group.setLayout(vector_layout)
        self.scroll_layout.addWidget(vector_group)

        # ========================
        # Conversion Tools
        # ========================
        conversion_group = QGroupBox("Conversion Tools")
        conversion_group.setCheckable(True)
        conversion_group.setChecked(False)
        conversion_layout = QVBoxLayout()

        # Polygon to Line
        btn_poly_to_line = QPushButton("Polygons to Lines")
        btn_poly_to_line.clicked.connect(self.polygons_to_lines)
        conversion_layout.addWidget(btn_poly_to_line)

        # Line Intersection Points
        btn_line_intersections = QPushButton("Generate Line Intersection Points")
        btn_line_intersections.clicked.connect(self.generate_line_intersections)
        conversion_layout.addWidget(btn_line_intersections)

        conversion_group.setLayout(conversion_layout)
        self.scroll_layout.addWidget(conversion_group)

        # ========================
        # Field Management
        # ========================
        field_group = QGroupBox("Field Management")
        field_group.setCheckable(True)
        field_group.setChecked(False)
        field_layout = QVBoxLayout()

        # Create a horizontal layout for the two field buttons
        field_button_layout = QHBoxLayout()

        # Bridge Fields Button
        self.btn_bridge_fields = QPushButton("Add Bridge Fields")
        self.btn_bridge_fields.setIcon(QIcon(":/images/themes/default/mActionNewTable.svg"))
        self.btn_bridge_fields.clicked.connect(self.add_bridge_fields)
        field_button_layout.addWidget(self.btn_bridge_fields)

        # Seamline Fields Button
        self.btn_seamline_fields = QPushButton("Add Seamline Fields")
        self.btn_seamline_fields.setIcon(QIcon(":/images/themes/default/mActionNewTable.svg"))
        self.btn_seamline_fields.clicked.connect(self.add_seamline_fields)
        field_button_layout.addWidget(self.btn_seamline_fields)

        field_layout.addLayout(field_button_layout)
        field_group.setLayout(field_layout)
        self.scroll_layout.addWidget(field_group)

        # ========================
        # Export Tools
        # ========================
        export_group = QGroupBox("Export Tools")
        export_group.setCheckable(True)
        export_group.setChecked(False)
        export_layout = QVBoxLayout()

        self.btn_export = QPushButton("Save Selected Features")
        self.btn_export.setIcon(QIcon(":/images/themes/default/mActionSaveEdits.svg"))
        self.btn_export.clicked.connect(self.save_selected_features)
        export_layout.addWidget(self.btn_export)

        export_group.setLayout(export_layout)
        self.scroll_layout.addWidget(export_group)

        # Add stretch to push tools to top
        self.scroll_layout.addStretch()

    # =========================================
    # CRS Handling
    # =========================================

    def get_selected_crs(self):
        """Get currently selected CRS with validation"""
        crs_text = self.global_crs_combo.currentText()
        crs = QgsCoordinateReferenceSystem()
        if not crs.createFromString(crs_text):
            QMessageBox.warning(self, "Invalid CRS", f"Invalid CRS specified: {crs_text}")
            return None

        # Ensure CRS uses meters for accurate measurements
        if crs.mapUnits() != QgsUnitTypes.DistanceMeters:
            QMessageBox.warning(
                self,
                "Invalid CRS Units",
                "Selected CRS must use meters as units for accurate measurements!\n"
                f"Current units: {QgsUnitTypes.toString(crs.mapUnits())}"
            )
            return None

        return crs

    # =========================================
    # Tool Implementations
    # =========================================

    def create_grid(self):
        """Create grid with precise measurements using QGIS algorithm"""
        try:
            spacing = float(self.grid_size_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid grid size in meters!")
            return

        # Get and validate CRS
        crs = self.get_selected_crs()
        if not crs:
            return

        # Get reference layer
        layer = self.iface.activeLayer()
        if not layer:
            QMessageBox.warning(self, "No Layer", "Please select a reference layer!")
            return

        # Transform extent to target CRS
        source_crs = layer.crs()
        transform = QgsCoordinateTransform(source_crs, crs, QgsProject.instance())
        extent = transform.transformBoundingBox(layer.extent())

        # Align to grid spacing
        xmin = spacing * math.floor(extent.xMinimum() / spacing)
        ymin = spacing * math.floor(extent.yMinimum() / spacing)
        xmax = spacing * math.ceil(extent.xMaximum() / spacing)
        ymax = spacing * math.ceil(extent.yMaximum() / spacing)

        # Ensure at least one cell
        if xmax <= xmin:
            xmax = xmin + spacing
        if ymax <= ymin:
            ymax = ymin + spacing

        # Get output path
        path, _ = QFileDialog.getSaveFileName(self, "Save Grid", "", "Shapefiles (*.shp)")
        if not path:
            return

        # Create grid using QGIS algorithm
        result = processing.run("native:creategrid", {
            'TYPE': 2,  # Rectangle (polygon)
            'EXTENT': f"{xmin},{xmax},{ymin},{ymax}",
            'HSPACING': spacing,
            'VSPACING': spacing,
            'HOVERLAY': 0,
            'VOVERLAY': 0,
            'CRS': crs,
            'OUTPUT': path
        })

        if 'OUTPUT' not in result:
            QMessageBox.critical(self, "Error", "Failed to create grid!")
            return

        # Load and display grid
        grid_layer = QgsVectorLayer(path, os.path.splitext(os.path.basename(path))[0], "ogr")
        if not grid_layer.isValid():
            QMessageBox.critical(self, "Error", "Failed to load grid layer!")
            return

        QgsProject.instance().addMapLayer(grid_layer)

        # Set project CRS for accurate measurement
        QgsProject.instance().setCrs(crs)
        self.iface.mapCanvas().setDestinationCrs(crs)
        self.iface.mapCanvas().refresh()

        # Zoom to layer for verification
        self.iface.mapCanvas().setExtent(grid_layer.extent())
        self.iface.mapCanvas().refresh()

        # Calculate grid dimensions
        cols = int(round((xmax - xmin) / spacing))
        rows = int(round((ymax - ymin) / spacing))

        QMessageBox.information(self, "Success",
                                f"{spacing}m grid created with {cols}x{rows} cells\n"
                                f"Output CRS: {crs.description()}")

    # Updated create_buffer method with smoother edges
    def create_buffer(self):
        """Create buffer with precise measurements and smoother edges"""
        try:
            distance = float(self.buffer_size_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid buffer distance in meters!")
            return

        # Get and validate CRS
        crs = self.get_selected_crs()
        if not crs:
            return

        layer = self.iface.activeLayer()
        if not layer or layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            QMessageBox.warning(self, "Invalid Layer", "Please select a polygon layer!")
            return

        # Reproject to target CRS first
        if layer.crs() != crs:
            reprojected_layer = processing.run("native:reprojectlayer", {
                'INPUT': layer,
                'TARGET_CRS': crs,
                'OUTPUT': 'memory:'
            })['OUTPUT']
            layer = reprojected_layer

        path, _ = QFileDialog.getSaveFileName(self, "Save Buffer", "", "Shapefiles (*.shp)")
        if not path:
            return

        layer_name = os.path.splitext(os.path.basename(path))[0]

        # Create buffer with smoother parameters
        processing.run("native:buffer", {
            'INPUT': layer,
            'DISTANCE': distance,
            'SEGMENTS': 50,  # Increased from 20 to 50 for smoother curves
            'END_CAP_STYLE': 0,  # Round cap
            'JOIN_STYLE': 1,  # Round join
            'MITER_LIMIT': 2,
            'DISSOLVE': False,
            'OUTPUT': path
        })

        buffer_layer = QgsVectorLayer(path, layer_name, "ogr")
        if not buffer_layer.isValid():
            QMessageBox.critical(self, "Error", "Failed to create buffer layer!")
            return

        QgsProject.instance().addMapLayer(buffer_layer)

        # Set project CRS for accurate measurement
        QgsProject.instance().setCrs(crs)
        self.iface.mapCanvas().setDestinationCrs(crs)
        self.iface.mapCanvas().refresh()

        # Zoom to layer for verification
        self.iface.mapCanvas().setExtent(buffer_layer.extent())
        self.iface.mapCanvas().refresh()

        QMessageBox.information(self, "Success",
                                f"{distance}m buffer created with smooth edges\n"
                                f"Output CRS: {crs.description()}")

    def create_vector_layer(self):
        """Create empty vector layer with proper CRS handling"""
        # Get selected geometry type
        geom_type = self.geom_combo.currentText()
        if geom_type == "Point":
            qgis_geom_type = QgsWkbTypes.Point
        elif geom_type == "Polygon":
            qgis_geom_type = QgsWkbTypes.Polygon
        else:
            QMessageBox.warning(self, "Invalid Geometry", "Please select a valid geometry type!")
            return

        # Get CRS
        crs = self.get_selected_crs()
        if not crs:
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save Vector Layer", "", "Shapefiles (*.shp)")
        if not path:
            return

        layer_name = os.path.splitext(os.path.basename(path))[0]

        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))

        writer = QgsVectorFileWriter(
            path, "UTF-8", fields,
            qgis_geom_type, crs, "ESRI Shapefile"
        )

        if writer.hasError() != QgsVectorFileWriter.NoError:
            QMessageBox.critical(self, "Error", f"File error: {writer.errorMessage()}")
            return

        del writer
        layer = QgsVectorLayer(path, layer_name, "ogr")
        QgsProject.instance().addMapLayer(layer)

        # Set project CRS for consistent measurements
        QgsProject.instance().setCrs(crs)
        self.iface.mapCanvas().setDestinationCrs(crs)
        self.iface.mapCanvas().refresh()

        QMessageBox.information(self, "Success",
                                f"{geom_type} layer created with CRS: {crs.description()}")

    def polygons_to_lines(self):
        """Convert polygons to lines"""
        layer = self.iface.activeLayer()
        if not layer or layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            QMessageBox.warning(self, "Invalid Layer", "Please select a polygon layer!")
            return

        # Get CRS
        crs = self.get_selected_crs()
        if not crs:
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save Lines Output", "", "Shapefiles (*.shp)")
        if not path:
            return

        layer_name = os.path.splitext(os.path.basename(path))[0]

        # Ensure layer is in correct CRS
        if layer.crs() != crs:
            # Create in-memory reprojected layer
            reprojected_layer = processing.run("native:reprojectlayer", {
                'INPUT': layer,
                'TARGET_CRS': crs,
                'OUTPUT': 'memory:'
            })['OUTPUT']
            layer = reprojected_layer

        processing.run("native:polygonstolines", {
            'INPUT': layer,
            'OUTPUT': path
        })

        line_layer = QgsVectorLayer(path, layer_name, "ogr")
        QgsProject.instance().addMapLayer(line_layer)

        # Set project CRS for consistent measurements
        QgsProject.instance().setCrs(crs)
        self.iface.mapCanvas().setDestinationCrs(crs)
        self.iface.mapCanvas().refresh()

        QMessageBox.information(self, "Success",
                                f"Lines created with CRS: {crs.description()}")

    def generate_line_intersections(self):
        """Generate intersection points from two line layers"""
        # Get all line layers
        line_layers = [layer for layer in QgsProject.instance().mapLayers().values()
                       if layer.type() == QgsVectorLayer.VectorLayer and
                       layer.geometryType() == QgsWkbTypes.LineGeometry]

        if len(line_layers) < 2:
            QMessageBox.warning(self, "Not Enough Layers", "Please load at least two line layers in the project!")
            return

        # Get CRS
        crs = self.get_selected_crs()
        if not crs:
            return

        # Get layer names
        layer_names = [layer.name() for layer in line_layers]

        # Let user select the two layers
        layer1_name, ok1 = QInputDialog.getItem(self, "Select First Line Layer",
                                                "Layer:", layer_names, 0, False)
        if not ok1 or not layer1_name:
            return

        layer2_name, ok2 = QInputDialog.getItem(self, "Select Second Line Layer",
                                                "Layer:", layer_names, 1, False)
        if not ok2 or not layer2_name:
            return

        # Find the actual layer objects
        layer1 = next(layer for layer in line_layers if layer.name() == layer1_name)
        layer2 = next(layer for layer in line_layers if layer.name() == layer2_name)

        # Get output path
        path, _ = QFileDialog.getSaveFileName(self, "Save Intersection Points", "", "Shapefiles (*.shp)")
        if not path:
            return

        layer_name = os.path.splitext(os.path.basename(path))[0]

        # Create intersection points
        processing.run("native:lineintersections", {
            'INPUT': layer1,
            'INTERSECT': layer2,
            'INPUT_FIELDS': [],
            'INTERSECT_FIELDS': [],
            'OUTPUT': path
        })

        intersection_layer = QgsVectorLayer(path, layer_name, "ogr")
        if intersection_layer.isValid():
            # Reproject to selected CRS if needed
            if intersection_layer.crs() != crs:
                reprojected_path = os.path.join(os.path.dirname(path), "temp_intersections.shp")
                processing.run("native:reprojectlayer", {
                    'INPUT': intersection_layer,
                    'TARGET_CRS': crs,
                    'OUTPUT': reprojected_path
                })
                intersection_layer = QgsVectorLayer(reprojected_path, layer_name, "ogr")

            QgsProject.instance().addMapLayer(intersection_layer)

            # Set project CRS for consistent measurements
            QgsProject.instance().setCrs(crs)
            self.iface.mapCanvas().setDestinationCrs(crs)
            self.iface.mapCanvas().refresh()

            QMessageBox.information(self, "Success",
                                    f"Intersection points created with CRS: {crs.description()}")
        else:
            QMessageBox.critical(self, "Error", "Failed to create intersection layer!")

    def add_bridge_fields(self):
        """Add standard bridge fields to layer including Rework field"""
        layer = self.iface.activeLayer()
        if not layer or layer.type() != QgsVectorLayer.VectorLayer:
            QMessageBox.warning(self, "Invalid Layer", "Please select a vector layer!")
            return

        # Define fields to add - including new "Rework" field
        new_fields = [
            ("Part", QVariant.Int),
            ("Assign", QVariant.String),
            ("Status", QVariant.String),
            ("Remarks", QVariant.String),
            ("QC", QVariant.String),
            ("QCRemarks", QVariant.String),
            ("Rework", QVariant.String)  # New field
        ]

        self._add_fields_to_layer(layer, new_fields, "Bridge")

    def add_seamline_fields(self):
        """Add seamline-specific fields to layer including standard fields"""
        layer = self.iface.activeLayer()
        if not layer or layer.type() != QgsVectorLayer.VectorLayer:
            QMessageBox.warning(self, "Invalid Layer", "Please select a vector layer!")
            return

        # Define fields to add - standard fields PLUS seamline-specific fields
        new_fields = [
            ("Part", QVariant.Int),
            ("Assign", QVariant.String),
            ("Status", QVariant.String),
            ("Remarks", QVariant.String),
            ("QC", QVariant.String),
            ("QCRemarks", QVariant.String),
            ("Rework", QVariant.String),  # New field
            ("Geo_Assign", QVariant.String),
            ("Geo_Stat", QVariant.String),
            ("Geo_QC", QVariant.String)
        ]

        self._add_fields_to_layer(layer, new_fields, "Seamline")

    def _add_fields_to_layer(self, layer, new_fields, field_type):
        """Helper function to add fields to a layer"""
        layer.startEditing()
        provider = layer.dataProvider()
        existing_fields = [field.name() for field in provider.fields()]
        added_fields = []

        for field_name, field_type in new_fields:
            if field_name not in existing_fields:
                provider.addAttributes([QgsField(field_name, field_type)])
                added_fields.append(field_name)

        layer.updateFields()

        if added_fields:
            layer.commitChanges()
            QMessageBox.information(
                self,
                "Fields Added",
                f"Added {len(added_fields)} {field_type} fields:\n{', '.join(added_fields)}"
            )
        else:
            layer.rollBack()
            QMessageBox.information(
                self,
                "No Fields Added",
                "All fields already exist in the layer."
            )

    def save_selected_features(self):
        """Save selected features to a new shapefile"""
        layer = self.iface.activeLayer()
        if not layer or layer.type() != QgsVectorLayer.VectorLayer:
            QMessageBox.warning(self, "Invalid Layer", "Please select a vector layer!")
            return

        selected_features = layer.selectedFeatures()
        if not selected_features:
            QMessageBox.warning(self, "No Selection", "No features selected!")
            return

        # Get output file path
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Selected Features",
            QgsProject.instance().homePath(),
            "Shapefiles (*.shp)"
        )
        if not output_path:
            return

        # Create save options
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = "ESRI Shapefile"
        save_options.fileEncoding = "UTF-8"
        save_options.onlySelectedFeatures = True

        # Write to new shapefile
        transform_context = QgsProject.instance().transformContext()

        # Capture all three return values
        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            output_path,
            transform_context,
            save_options
        )

        # Unpack the result
        error_code = result[0]
        error_message = result[1]

        if error_code != QgsVectorFileWriter.NoError:
            QMessageBox.critical(self, "Save Error",
                                 f"Failed to save features:\n{error_message}")
            return

        # Load the saved layer
        saved_layer = QgsVectorLayer(output_path, os.path.splitext(os.path.basename(output_path))[0], "ogr")
        if saved_layer.isValid():
            QgsProject.instance().addMapLayer(saved_layer)
            QMessageBox.information(self, "Success",
                                    f"Saved {len(selected_features)} features to:\n{output_path}")
        else:
            QMessageBox.warning(self, "Load Error",
                                "Features saved successfully but could not load the layer.")

    def set_production_status(self, status):
        """Set production status for selected features"""
        self.update_attribute("Status", status, "production status")

    def set_production_remarks(self, remark):
        """Set production remarks for selected features"""
        self.update_attribute("Remarks", remark, "production remarks")

    def set_qc_status(self, status):
        """Set QC status for selected features"""
        self.update_attribute("QC", status, "QC status")

    def set_qc_remarks(self, remark):
        """Set QC remarks for selected features"""
        self.update_attribute("QCRemarks", remark, "QC remarks")

    def update_attribute(self, field_name, value, description):
        """Generic method to update attributes"""
        layer = self.iface.activeLayer()
        if not layer or layer.type() != QgsVectorLayer.VectorLayer:
            QMessageBox.warning(self, "Invalid Layer", "Please select a vector layer!")
            return

        field_index = layer.fields().indexFromName(field_name)
        if field_index == -1:
            QMessageBox.warning(self, "Missing Field", f"'{field_name}' field not found!")
            return

        selected = layer.selectedFeatures()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select features first!")
            return

        layer.startEditing()
        for feature in selected:
            layer.changeAttributeValue(feature.id(), field_index, value)
        layer.commitChanges()

        self.iface.messageBar().pushSuccess(
            f"{field_name} Updated",
            f"Set {description} for {len(selected)} features to '{value}'"
        )


class PhotogrammetryToolsPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.dock_widget = None

    def initGui(self):
        self.dock_widget = PhotogrammetryToolsDock(self.iface)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

        self.menu = QAction("Photogrammetry Tools")
        self.menu.triggered.connect(self.toggle_dock_visibility)
        self.iface.addPluginToMenu("&Photogrammetry Tools", self.menu)

    def unload(self):
        if self.dock_widget:
            self.iface.removeDockWidget(self.dock_widget)
            self.dock_widget.deleteLater()
            self.dock_widget = None

        self.iface.removePluginMenu("&Photogrammetry Tools", self.menu)
        del self.menu

    def toggle_dock_visibility(self):
        if self.dock_widget:
            self.dock_widget.setVisible(not self.dock_widget.isVisible())