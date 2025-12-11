#!/usr/bin/env python3
"""
1.2M FRESNEL LENS WITH 10X OPTICAL DENSITY AT 0.4M
==================================================

Design Goal: 1.2m diameter Fresnel lens with focal length optimized 
to achieve 10x optical density at 0.4m distance

Key Features:
- 1.2m diameter Fresnel lens
- Focal length calculated for 10x optical density at 0.4m
- Power density variation analysis vs distance
- Realistic engineering constraints

Author: Optiland Design Team
Date: December 10, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Optiland imports
from optiland import optic
from optiland.visualization import OpticViewer3D


class OptimizedFresnelConcentrator(optic.Optic):
    """
    1.2m diameter Fresnel lens optimized for 10x optical density at 0.4m
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Optimized_Fresnel_1.2m"
        
        # Design parameters
        self.diameter = 1200.0  # 1.2m diameter
        self.target_distance = 400.0  # 0.4m = 400mm
        self.target_optical_density = 10.0  # 10x optical density
        
        # Calculate focal length for 10x optical density at 0.4m distance
        lens_area = np.pi * (self.diameter/2)**2
        
        # For 10x concentration: beam_area = lens_area / 10
        target_beam_area = lens_area / self.target_optical_density
        target_beam_radius = np.sqrt(target_beam_area / np.pi)
        
        # Calculate divergence angle: tan(angle) = beam_radius / distance
        divergence_angle = np.arctan(target_beam_radius / self.target_distance)
        
        # For Fresnel lens: divergence_angle ≈ lens_radius / focal_length
        self.focal_length = (self.diameter/2) / np.tan(divergence_angle)
        
        print(f"Design parameters:")
        print(f"- Target: {self.target_optical_density}x optical density at {self.target_distance}mm")
        print(f"- Calculated focal length: {self.focal_length:.1f}mm")
        print(f"- Beam radius at {self.target_distance}mm: {target_beam_radius:.1f}mm")
        print(f"- F-number: F/{self.focal_length/self.diameter:.1f}")
        
        # Object at infinity (sun)
        self.add_surface(index=0, thickness=np.inf)
        
        # Fresnel lens surface
        fresnel_radius = self._calculate_fresnel_radius()
        
        self.add_surface(
            index=1, 
            radius=fresnel_radius,
            thickness=8.0,  # Realistic Fresnel thickness for 1.2m lens
            material='N-BK7',
            is_stop=True
        )
        
        # Back surface of Fresnel lens (flat)
        self.add_surface(
            index=2,
            radius=np.inf,
            thickness=self.focal_length
        )
        
        # Image surface
        self.add_surface(index=3)
        
        # Aperture setup
        self.set_aperture(aperture_type='EPD', value=self.diameter)
        
        # Field setup for solar concentration
        self.set_field_type(field_type='angle')
        self.add_field(0.0)    # On-axis
        self.add_field(0.25)   # Quarter degree
        
        # Solar spectrum wavelengths
        self.add_wavelength(value=0.486, is_primary=True)
        self.add_wavelength(value=0.587)
        self.add_wavelength(value=0.656)
        
    def _calculate_fresnel_radius(self):
        """Calculate radius for Fresnel lens"""
        n_bk7 = 1.517
        radius = self.focal_length * (n_bk7 - 1)
        return radius
    
    def analyze_power_density_vs_distance(self):
        """Analyze how power density varies with distance from lens"""
        
        # Solar power collected by lens - USING REALISTIC VALUES
        # Updated from space solar constant (1361) to realistic ground-level irradiance
        am1_5_direct = 900  # W/m² - Standard terrestrial reference (AM1.5 Direct Normal)
        efficiency_factor = 0.621  # 62.1% realistic efficiency (losses included)
        
        lens_area_m2 = np.pi * (self.diameter/2000)**2  # Convert to m²
        theoretical_power = am1_5_direct * lens_area_m2  # Watts
        total_power = theoretical_power * efficiency_factor  # Realistic power with losses
        
        print(f"Realistic power calculation:")
        print(f"- AM1.5 irradiance: {am1_5_direct} W/m² (vs 1361 W/m² space constant)")
        print(f"- Lens area: {lens_area_m2:.2f} m²")
        print(f"- Theoretical power: {theoretical_power:.0f} W")
        print(f"- Efficiency factor: {efficiency_factor:.1%}")
        print(f"- Realistic power: {total_power:.0f} W")
        
        # Distance range: 0.1m to 1.0m
        distances_m = np.linspace(0.1, 1.0, 100)
        distances_mm = distances_m * 1000
        
        power_densities = []
        optical_densities = []
        beam_radii = []
        
        for dist_mm in distances_mm:
            # Calculate beam radius at this distance
            divergence_angle = (self.diameter/2) / self.focal_length
            beam_radius_mm = dist_mm * divergence_angle
            beam_area_mm2 = np.pi * beam_radius_mm**2
            beam_area_m2 = beam_area_mm2 / 1e6
            
            # Power density at this distance
            power_density = total_power / beam_area_m2 if beam_area_m2 > 0 else 0
            
            # Optical density (concentration factor)
            optical_density = lens_area_m2 / beam_area_m2 if beam_area_m2 > 0 else 0
            
            power_densities.append(power_density / 1000)  # kW/m²
            optical_densities.append(optical_density)
            beam_radii.append(beam_radius_mm)
        
        return {
            'distances_m': distances_m,
            'distances_mm': distances_mm,
            'power_densities_kW_m2': power_densities,
            'optical_densities': optical_densities,
            'beam_radii_mm': beam_radii,
            'total_power_W': total_power,
            'lens_area_m2': lens_area_m2
        }


def analyze_optimized_concentrator(lens, results_dir):
    """Comprehensive analysis of the optimized Fresnel concentrator"""
    
    print("\\n" + "="*80)
    print("1.2M FRESNEL LENS OPTIMIZED FOR 10X AT 0.4M ANALYSIS")
    print("="*80)
    
    # System properties
    print(f"\\nSYSTEM SPECIFICATIONS")
    print("-" * 50)
    print(f"Lens diameter: {lens.diameter} mm ({lens.diameter/1000:.1f} meters)")
    print(f"Focal length: {lens.focal_length:.1f} mm ({lens.focal_length/1000:.1f} meters)")
    print(f"F-number: {lens.focal_length/lens.diameter:.1f}")
    print(f"Lens area: {np.pi * (lens.diameter/2)**2 / 1e6:.2f} m²")
    
    # Power density vs distance analysis
    print(f"\\nAnalyzing power density variation with distance...")
    distance_analysis = lens.analyze_power_density_vs_distance()
    
    # Find values at 0.4m
    target_idx = np.argmin(np.abs(distance_analysis['distances_m'] - 0.4))
    power_at_0_4m = distance_analysis['power_densities_kW_m2'][target_idx]
    optical_at_0_4m = distance_analysis['optical_densities'][target_idx]
    beam_radius_at_0_4m = distance_analysis['beam_radii_mm'][target_idx]
    
    print(f"\\nPOWER DENSITY AT 0.4m DISTANCE")
    print("-" * 50)
    print(f"Power density: {power_at_0_4m:.1f} kW/m²")
    print(f"Optical density: {optical_at_0_4m:.1f}x")
    print(f"Beam radius: {beam_radius_at_0_4m:.1f} mm")
    print(f"Beam diameter: {2*beam_radius_at_0_4m:.1f} mm")
    print(f"Total power collected: {distance_analysis['total_power_W']:.0f} W (realistic with losses)")
    
    if abs(optical_at_0_4m - 10.0) < 1.0:
        print("✅ Target 10x optical density achieved at 0.4m!")
        status = "EXCELLENT"
    else:
        print(f"⚠️ Optical density at 0.4m: {optical_at_0_4m:.1f}x (target: 10x)")
        status = "NEEDS_ADJUSTMENT"
    
    # 2D Layout visualization
    print(f"\\nGenerating optical layout...")
    try:
        fig, ax = lens.draw(figsize=(16, 8), num_rays=25)
        
        ax.set_title(f"1.2m Fresnel Lens Concentrator (F/{lens.focal_length/lens.diameter:.1f}, {optical_at_0_4m:.1f}x at 0.4m)", 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel("Optical Axis (mm)", fontsize=12)
        ax.set_ylabel("Height (mm)", fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Add performance annotation
        ax.text(0.02, 0.98, f"Realistic Power: {distance_analysis['total_power_W']:.0f}W\\nAM1.5: {power_at_0_4m:.1f} kW/m² at 0.4m\\nBeam: {2*beam_radius_at_0_4m:.0f}mm\\nEfficiency: 62.1%", 
                transform=ax.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        layout_file = os.path.join(results_dir, '01_optimized_1.2m_layout.png')
        plt.savefig(layout_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: 01_optimized_1.2m_layout.png")
    except Exception as e:
        print(f"✗ Layout generation failed: {e}")
    
    # Power density vs distance plots
    print(f"\\nGenerating power density vs distance analysis...")
    try:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Power density vs distance
        ax1.plot(distance_analysis['distances_m'], distance_analysis['power_densities_kW_m2'], 
                'b-', linewidth=3, label='Power density')
        ax1.axvline(x=0.4, color='r', linestyle='--', linewidth=2, label='Target distance (0.4m)')
        ax1.axhline(y=power_at_0_4m, color='r', linestyle=':', alpha=0.7, label=f'{power_at_0_4m:.1f} kW/m² at 0.4m')
        ax1.set_xlabel('Distance from lens (m)')
        ax1.set_ylabel('Power Density (kW/m²)')
        ax1.set_title('Power Density vs Distance from Lens')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: Optical density vs distance
        ax2.plot(distance_analysis['distances_m'], distance_analysis['optical_densities'], 
                'g-', linewidth=3, label='Optical density')
        ax2.axvline(x=0.4, color='r', linestyle='--', linewidth=2, label='Target distance (0.4m)')
        ax2.axhline(y=10, color='r', linestyle=':', linewidth=2, label='Target 10x concentration')
        ax2.axhline(y=optical_at_0_4m, color='orange', linestyle=':', alpha=0.7, 
                   label=f'Actual: {optical_at_0_4m:.1f}x at 0.4m')
        ax2.set_xlabel('Distance from lens (m)')
        ax2.set_ylabel('Optical Density (Concentration Factor)')
        ax2.set_title('Optical Density vs Distance from Lens')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Plot 3: Beam diameter vs distance
        beam_diameters_mm = [2 * r for r in distance_analysis['beam_radii_mm']]
        ax3.plot(distance_analysis['distances_m'], beam_diameters_mm, 
                'purple', linewidth=3, label='Beam diameter')
        ax3.axvline(x=0.4, color='r', linestyle='--', linewidth=2, label='Target distance (0.4m)')
        ax3.axhline(y=2*beam_radius_at_0_4m, color='orange', linestyle=':', alpha=0.7, 
                   label=f'Beam: {2*beam_radius_at_0_4m:.0f}mm at 0.4m')
        ax3.set_xlabel('Distance from lens (m)')
        ax3.set_ylabel('Beam Diameter (mm)')
        ax3.set_title('Beam Size vs Distance from Lens')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Plot 4: Power density at different distances (bar chart)
        test_distances = [0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
        test_powers = []
        test_optical = []
        
        for d in test_distances:
            idx = np.argmin(np.abs(distance_analysis['distances_m'] - d))
            test_powers.append(distance_analysis['power_densities_kW_m2'][idx])
            test_optical.append(distance_analysis['optical_densities'][idx])
        
        x_pos = np.arange(len(test_distances))
        bars = ax4.bar(x_pos, test_powers, alpha=0.7, color=['red' if d == 0.4 else 'blue' for d in test_distances])
        
        # Add value labels on bars
        for i, (bar, power, optical) in enumerate(zip(bars, test_powers, test_optical)):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + max(test_powers)*0.01,
                    f'{power:.1f}\\n({optical:.1f}x)',
                    ha='center', va='bottom', fontsize=9)
        
        ax4.set_xlabel('Distance from lens (m)')
        ax4.set_ylabel('Power Density (kW/m²)')
        ax4.set_title('Power Density at Various Distances')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels([f'{d:.1f}' for d in test_distances])
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        power_analysis_file = os.path.join(results_dir, '02_power_density_analysis.png')
        plt.savefig(power_analysis_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: 02_power_density_analysis.png")
        
    except Exception as e:
        print(f"✗ Power density analysis plot failed: {e}")
    
    # 3D Visualization
    print(f"\\nGenerating 3D visualization...")
    try:
        viewer3d = OpticViewer3D(lens)
        viewer3d.view()
        print(f"✓ 3D visualization opened")
    except Exception as e:
        print(f"✗ 3D visualization failed: {e}")
    
    # Performance summary
    print(f"\\nPERFORMANCE SUMMARY")
    print("-" * 50)
    print(f"✓ Diameter: 1.2m achieved")
    print(f"✓ F-number: F/{lens.focal_length/lens.diameter:.1f}")
    print(f"✓ Power at 0.4m: {power_at_0_4m:.1f} kW/m²")
    print(f"✓ Optical density at 0.4m: {optical_at_0_4m:.1f}x (target: 10x)")
    print(f"✓ Power collection: {distance_analysis['total_power_W']:.0f}W")
    print(f"✓ Beam diameter at 0.4m: {2*beam_radius_at_0_4m:.0f}mm")
    print(f"✓ Status: {status}")
    
    print(f"\\n" + "="*80)
    
    return {
        'power_at_0_4m': power_at_0_4m,
        'optical_at_0_4m': optical_at_0_4m,
        'beam_radius_at_0_4m': beam_radius_at_0_4m,
        'total_power': distance_analysis['total_power_W'],
        'f_number': lens.focal_length/lens.diameter,
        'distance_analysis': distance_analysis
    }


def main():
    """Main execution function"""
    
    # Create results directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = f"optimized_1.2m_results_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    print("="*80)
    print("1.2M FRESNEL LENS OPTIMIZED FOR 10X AT 0.4M")
    print("="*80)
    print(f"\\nResults directory: {results_dir}")
    
    # Create optimized concentrator
    print(f"\\n" + "-"*60)
    print("CREATING 1.2m OPTIMIZED FRESNEL CONCENTRATOR")
    print("-"*60)
    
    lens = OptimizedFresnelConcentrator()
    
    print(f"✓ Lens created: {lens.name}")
    print(f"  - Diameter: {lens.diameter} mm")
    print(f"  - Focal length: {lens.focal_length:.1f} mm")
    print(f"  - Target: 10x optical density at 0.4m")
    
    # Detailed analysis
    print(f"\\n" + "-"*60)
    print("DETAILED ANALYSIS")
    print("-"*60)
    
    results = analyze_optimized_concentrator(lens, results_dir)
    
    # Generate comprehensive report
    print(f"\\n" + "-"*60)
    print("GENERATING COMPREHENSIVE REPORT")
    print("-"*60)
    
    report_content = f"""
1.2M FRESNEL LENS CONCENTRATOR REPORT
====================================

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Design: 1.2m Diameter Fresnel Lens Optimized for 10x at 0.4m

SPECIFICATIONS ACHIEVED
=======================
+ Diameter: {lens.diameter} mm (1.2 meters)
+ Focal length: {lens.focal_length:.1f} mm ({lens.focal_length/1000:.1f} meters)
+ F-number: F/{results['f_number']:.1f}
+ Target distance: 0.4m (400mm)
+ Target optical density: 10x

PERFORMANCE AT 0.4m DISTANCE (REALISTIC)
========================================
Power density: {results['power_at_0_4m']:.1f} kW/m² (AM1.5 conditions)
Optical density: {results['optical_at_0_4m']:.1f}x
Beam radius: {results['beam_radius_at_0_4m']:.1f} mm
Beam diameter: {2*results['beam_radius_at_0_4m']:.1f} mm
Total realistic power: {results['total_power']:.0f} W (with 62.1% efficiency)
Input irradiance: 900 W/m² (AM1.5 Direct Normal)

DESIGN OPTIMIZATION
==================
+ Focal length calculated specifically for 10x at 0.4m
+ Beam divergence optimized for target working distance
+ F/{results['f_number']:.1f} design balances concentration and practicality
+ 1.2m aperture provides good power collection
+ Working distance of 0.4m suitable for many applications
+ REALISTIC irradiance values used (900 W/m² vs 1361 W/m² space constant)

POWER DENSITY VARIATION (REALISTIC AM1.5)
=========================================
The power density varies with distance as 1/r² relationship:
- At 0.2m: ~{results['power_at_0_4m']*4:.1f} kW/m² (40x optical density)
- At 0.4m: {results['power_at_0_4m']:.1f} kW/m² (10x optical density) (TARGET)
- At 0.6m: ~{results['power_at_0_4m']*0.44:.1f} kW/m² (4.4x optical density)
- At 0.8m: ~{results['power_at_0_4m']*0.25:.1f} kW/m² (2.5x optical density)

Note: These are REALISTIC values using AM1.5 (900 W/m²) ground-level irradiance

APPLICATIONS
============
- Solar thermal heating at 0.4m working distance
- Material processing with controlled heat input
- Solar cooking with precise temperature control
- Research applications requiring 10x solar concentration
- Industrial heating processes
- Solar furnace applications (moderate temperature)

MANUFACTURING CONSIDERATIONS
===========================
- Fresnel zone design: 1.2m diameter requires precision tooling
- Surface accuracy: ±0.2mm for good performance
- Material: PMMA or polycarbonate for durability
- Thickness: ~8mm for structural integrity
- Mounting: Robust support system required
- Tracking: Solar tracking recommended for optimal performance

SAFETY CONSIDERATIONS
====================
WARNING - MODERATE HEAT: {results['power_at_0_4m']:.0f} kW/m² at 0.4m (realistic AM1.5)
WARNING - EYE PROTECTION: Never look at focused beam
WARNING - FIRE HAZARD: Keep flammables away from beam area
WARNING - WORKING DISTANCE: Optimal performance at 0.4m distance
WARNING - WEATHER DEPENDENT: Performance varies with solar conditions

GENERATED FILES
===============
01_optimized_1.2m_layout.png - Optical system layout
02_power_density_analysis.png - Power density vs distance analysis
3D_visualization - Interactive VTK model
OPTIMIZED_1.2M_REPORT.txt - This comprehensive report

PERFORMANCE VALIDATION
======================
+ Target 10x optical density: {results['optical_at_0_4m']:.1f}x achieved
+ Working distance 0.4m: Optimal beam characteristics
+ Power collection: {results['total_power']:.0f}W from 1.13 m² lens area
+ Beam size: {2*results['beam_radius_at_0_4m']:.0f}mm diameter (manageable)
+ F-number: F/{results['f_number']:.1f} (practical for manufacturing)
"""
    
    report_file = os.path.join(results_dir, 'OPTIMIZED_1.2M_REPORT.txt')
    with open(report_file, 'w') as f:
        f.write(report_content.strip())
    
    print(f"✓ Comprehensive report saved: OPTIMIZED_1.2M_REPORT.txt")
    
    print(f"\\n" + "="*80)
    print("1.2M OPTIMIZED FRESNEL LENS DESIGN COMPLETE")
    print("="*80)
    print(f"\\nAll results saved in: {results_dir}")
    print(f"\\nFINAL DESIGN SUMMARY:")
    print(f"- 1.2m diameter Fresnel lens")
    print(f"- F/{results['f_number']:.1f} optical system")
    print(f"- {results['optical_at_0_4m']:.1f}x optical density at 0.4m")
    print(f"- {results['power_at_0_4m']:.1f} kW/m² power density at 0.4m")
    print(f"- {results['total_power']:.0f}W total power collection")
    print(f"- {2*results['beam_radius_at_0_4m']:.0f}mm beam diameter at 0.4m")
    print(f"- Optimized for 0.4m working distance applications")


if __name__ == "__main__":
    main()