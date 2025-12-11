#!/usr/bin/env python3
"""
REALISTIC SOLAR POWER ANALYSIS FOR FRESNEL CONCENTRATORS
========================================================

This script analyzes realistic solar irradiance values and their impact on
Fresnel lens concentrator performance, accounting for real-world conditions.

Power Input Sources:
- Solar constant in space: 1361 W/m² (what I was using)
- AM1.5 Direct Normal Irradiance: 900 W/m² (realistic ground level)
- Peak sun conditions: 1000 W/m² (standard test conditions)
- Typical clear day: 700-800 W/m²
- Partly cloudy: 400-600 W/m²

Author: Optiland Design Team  
Date: December 11, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Optiland imports
from optiland import optic
from optiland.visualization import OpticViewer3D


class RealisticPowerAnalysis:
    """Analysis of realistic solar power conditions for concentrators"""
    
    def __init__(self):
        # Realistic solar irradiance values (W/m²)
        self.irradiance_conditions = {
            'space_solar_constant': 1361,     # Solar constant in space (my previous value)
            'am1_5_direct': 900,              # AM1.5 Direct Normal Irradiance (realistic)
            'peak_sun_conditions': 1000,      # Standard Test Conditions (STC)
            'excellent_clear_day': 800,       # Excellent clear day conditions
            'typical_clear_day': 700,         # Typical clear day
            'partly_cloudy': 500,             # Partly cloudy conditions
            'heavy_overcast': 200             # Heavy overcast (low performance)
        }
        
        # Efficiency factors
        self.efficiency_factors = {
            'optical_transmission': 0.90,     # 90% transmission through Fresnel lens
            'coating_losses': 0.95,           # 95% efficiency with AR coatings  
            'surface_errors': 0.85,           # 85% efficiency due to surface imperfections
            'tracking_accuracy': 0.95,        # 95% efficiency with good tracking
            'dust_soiling': 0.90              # 90% efficiency with regular cleaning
        }
        
        # Combined realistic efficiency
        self.total_efficiency = np.prod(list(self.efficiency_factors.values()))
        print(f"Total realistic efficiency: {self.total_efficiency:.1%}")
        
    def analyze_power_scenarios(self, lens_diameter_m=1.2):
        """Analyze power collection under different conditions"""
        
        results = {}
        lens_area = np.pi * (lens_diameter_m/2)**2  # m²
        
        print(f"\\nPOWER ANALYSIS FOR {lens_diameter_m}m DIAMETER LENS")
        print("="*60)
        print(f"Lens area: {lens_area:.2f} m²")
        print(f"Combined efficiency: {self.total_efficiency:.1%}\\n")
        
        for condition, irradiance in self.irradiance_conditions.items():
            # Theoretical power (perfect conditions)
            theoretical_power = irradiance * lens_area
            
            # Realistic power (with all efficiency losses)
            realistic_power = theoretical_power * self.total_efficiency
            
            results[condition] = {
                'irradiance_W_m2': irradiance,
                'theoretical_power_W': theoretical_power,
                'realistic_power_W': realistic_power,
                'efficiency_loss_W': theoretical_power - realistic_power
            }
            
            print(f"{condition.replace('_', ' ').title()}")
            print(f"  Input irradiance: {irradiance} W/m²")
            print(f"  Theoretical power: {theoretical_power:.0f} W")
            print(f"  Realistic power: {realistic_power:.0f} W")
            print(f"  Efficiency loss: {theoretical_power - realistic_power:.0f} W ({(1-self.total_efficiency)*100:.0f}%)")
            print()
            
        return results


class RealisticFresnelConcentrator(optic.Optic):
    """1.2m Fresnel lens with realistic power analysis"""
    
    def __init__(self, irradiance_condition='am1_5_direct'):
        super().__init__()
        self.name = "Realistic_Power_Fresnel_1.2m"
        
        # Initialize power analysis
        self.power_analysis = RealisticPowerAnalysis()
        self.irradiance_condition = irradiance_condition
        self.irradiance = self.power_analysis.irradiance_conditions[irradiance_condition]
        
        # Design parameters  
        self.diameter = 1200.0  # 1.2m diameter
        self.target_distance = 400.0  # 0.4m
        self.target_optical_density = 10.0
        
        print(f"\\nDESIGN PARAMETERS")
        print(f"Selected irradiance condition: {irradiance_condition}")
        print(f"Input irradiance: {self.irradiance} W/m² (vs 1361 W/m² I was using)")
        
        # Calculate focal length for 10x optical density at 0.4m
        lens_area = np.pi * (self.diameter/2)**2
        target_beam_area = lens_area / self.target_optical_density
        target_beam_radius = np.sqrt(target_beam_area / np.pi)
        divergence_angle = np.arctan(target_beam_radius / self.target_distance)
        self.focal_length = (self.diameter/2) / np.tan(divergence_angle)
        
        print(f"Focal length: {self.focal_length:.1f}mm")
        print(f"F-number: F/{self.focal_length/self.diameter:.1f}")
        
        # Build optical system (same as before)
        self.add_surface(index=0, thickness=np.inf)
        
        fresnel_radius = self.focal_length * (1.517 - 1)  # N-BK7
        self.add_surface(
            index=1, 
            radius=fresnel_radius,
            thickness=8.0,
            material='N-BK7',
            is_stop=True
        )
        
        self.add_surface(index=2, radius=np.inf, thickness=self.focal_length)
        self.add_surface(index=3)
        
        # Setup aperture and fields
        self.set_aperture(aperture_type='EPD', value=self.diameter)
        self.set_field_type(field_type='angle')
        self.add_field(0.0)
        self.add_field(0.25)
        
        # Solar spectrum
        self.add_wavelength(value=0.486, is_primary=True)
        self.add_wavelength(value=0.587)
        self.add_wavelength(value=0.656)
    
    def analyze_realistic_power_performance(self):
        """Analyze performance under realistic power conditions"""
        
        # Get power scenarios
        power_scenarios = self.power_analysis.analyze_power_scenarios(self.diameter/1000)
        
        # Calculate performance at 0.4m for each scenario
        lens_area_m2 = np.pi * (self.diameter/2000)**2
        divergence_angle = (self.diameter/2) / self.focal_length
        beam_radius_at_400mm = 400.0 * divergence_angle  # mm
        beam_area_at_400mm = np.pi * (beam_radius_at_400mm/1000)**2  # m²
        
        results = {}
        
        print(f"\\nPERFORMANCE AT 0.4m DISTANCE UNDER DIFFERENT CONDITIONS")
        print("="*80)
        
        for condition, power_data in power_scenarios.items():
            realistic_power = power_data['realistic_power_W']
            power_density = realistic_power / beam_area_at_400mm / 1000  # kW/m²
            optical_density = lens_area_m2 / beam_area_at_400mm
            
            results[condition] = {
                'power_density_kW_m2': power_density,
                'optical_density': optical_density,
                'realistic_power_W': realistic_power,
                'irradiance': power_data['irradiance_W_m2']
            }
            
            print(f"{condition.replace('_', ' ').title()}")
            print(f"  Input: {power_data['irradiance_W_m2']} W/m²")
            print(f"  Power at 0.4m: {power_density:.1f} kW/m² (vs {power_density * 1361/power_data['irradiance_W_m2']:.1f} with my 1361 W/m²)")
            print(f"  Collected power: {realistic_power:.0f} W")
            print(f"  Optical density: {optical_density:.1f}x")
            print()
            
        return results


def create_power_comparison_analysis():
    """Create comprehensive power comparison analysis"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = f"realistic_power_analysis_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    print("="*80)
    print("REALISTIC SOLAR POWER ANALYSIS FOR FRESNEL CONCENTRATORS")
    print("="*80)
    print(f"Results directory: {results_dir}\\n")
    
    # Initialize power analysis
    power_analysis = RealisticPowerAnalysis()
    
    # Test different conditions
    test_conditions = ['space_solar_constant', 'am1_5_direct', 'peak_sun_conditions', 'typical_clear_day']
    
    all_results = {}
    
    for condition in test_conditions:
        print(f"\\n{'='*60}")
        print(f"ANALYZING: {condition.replace('_', ' ').title()}")
        print(f"{'='*60}")
        
        # Create concentrator for this condition
        lens = RealisticFresnelConcentrator(irradiance_condition=condition)
        
        # Analyze performance  
        performance = lens.analyze_realistic_power_performance()
        all_results[condition] = performance[condition]
    
    # Create comparison plots
    print(f"\\n{'='*60}")
    print("CREATING COMPARISON VISUALIZATIONS")
    print(f"{'='*60}")
    
    try:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        conditions = list(all_results.keys())
        condition_labels = [c.replace('_', ' ').title() for c in conditions]
        irradiances = [all_results[c]['irradiance'] for c in conditions]
        power_densities = [all_results[c]['power_density_kW_m2'] for c in conditions]
        collected_powers = [all_results[c]['realistic_power_W'] for c in conditions]
        
        # Plot 1: Input irradiance comparison
        bars1 = ax1.bar(range(len(conditions)), irradiances, 
                       color=['red', 'orange', 'yellow', 'lightblue'], alpha=0.7)
        ax1.set_xlabel('Irradiance Conditions')
        ax1.set_ylabel('Solar Irradiance (W/m²)')
        ax1.set_title('Input Solar Irradiance: Realistic vs Space Conditions')
        ax1.set_xticks(range(len(conditions)))
        ax1.set_xticklabels(condition_labels, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, irr in zip(bars1, irradiances):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 20,
                    f'{irr} W/m²', ha='center', va='bottom', fontsize=10)
        
        # Plot 2: Power density at 0.4m
        bars2 = ax2.bar(range(len(conditions)), power_densities,
                       color=['red', 'orange', 'yellow', 'lightblue'], alpha=0.7)
        ax2.set_xlabel('Irradiance Conditions')
        ax2.set_ylabel('Power Density at 0.4m (kW/m²)')
        ax2.set_title('Power Density at 0.4m: Effect of Realistic Irradiance')
        ax2.set_xticks(range(len(conditions)))
        ax2.set_xticklabels(condition_labels, rotation=45, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, pd in zip(bars2, power_densities):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                    f'{pd:.1f}', ha='center', va='bottom', fontsize=10)
        
        # Plot 3: Collected power comparison  
        bars3 = ax3.bar(range(len(conditions)), collected_powers,
                       color=['red', 'orange', 'yellow', 'lightblue'], alpha=0.7)
        ax3.set_xlabel('Irradiance Conditions')
        ax3.set_ylabel('Total Power Collected (W)')
        ax3.set_title('Total Power Collection: 1.2m Fresnel Lens')
        ax3.set_xticks(range(len(conditions)))
        ax3.set_xticklabels(condition_labels, rotation=45, ha='right')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, power in zip(bars3, collected_powers):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 20,
                    f'{power:.0f}W', ha='center', va='bottom', fontsize=10)
        
        # Plot 4: Efficiency comparison (show what I was overestimating)
        my_original_values = [13.6 for _ in conditions]  # What I calculated with 1361 W/m²
        realistic_values = power_densities
        
        x = np.arange(len(conditions))
        width = 0.35
        
        bars4a = ax4.bar(x - width/2, my_original_values, width, 
                        label='My Original (1361 W/m²)', alpha=0.7, color='lightcoral')
        bars4b = ax4.bar(x + width/2, realistic_values, width,
                        label='Realistic Conditions', alpha=0.7, color='lightblue')
        
        ax4.set_xlabel('Irradiance Conditions')
        ax4.set_ylabel('Power Density at 0.4m (kW/m²)')
        ax4.set_title('Original vs Realistic Power Density Estimates')
        ax4.set_xticks(x)
        ax4.set_xticklabels(condition_labels, rotation=45, ha='right')
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.legend()
        
        # Add percentage differences
        for i, (orig, real) in enumerate(zip(my_original_values, realistic_values)):
            diff_pct = (orig - real) / real * 100
            ax4.text(i, max(orig, real) + 0.3, f'+{diff_pct:.0f}%', 
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        comparison_file = os.path.join(results_dir, 'realistic_power_comparison.png')
        plt.savefig(comparison_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: realistic_power_comparison.png")
        
    except Exception as e:
        print(f"✗ Comparison plot failed: {e}")
    
    # Generate comprehensive report
    print(f"\\n{'='*60}")
    print("GENERATING REALISTIC POWER REPORT")
    print(f"{'='*60}")
    
    report_content = f"""
REALISTIC SOLAR POWER ANALYSIS REPORT
====================================

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis: Realistic vs Theoretical Solar Irradiance Values

PROBLEM IDENTIFIED
==================
I was using: 1361 W/m² (solar constant in space)
Should use: 700-1000 W/m² (realistic ground-level conditions)

Overestimation factor: 36-94% too high depending on conditions

REALISTIC SOLAR IRRADIANCE VALUES
=================================
Space (Solar Constant): 1361 W/m² (what I used)
AM1.5 Direct Normal: 900 W/m² (standard terrestrial reference)
Peak Sun Conditions: 1000 W/m² (Standard Test Conditions)
Excellent Clear Day: 800 W/m² (realistic best case)
Typical Clear Day: 700 W/m² (common good weather)
Partly Cloudy: 500 W/m² (variable conditions)
Heavy Overcast: 200 W/m² (poor conditions)

EFFICIENCY FACTORS INCLUDED
===========================
Optical transmission: 90% (Fresnel lens material losses)
Coating losses: 95% (AR coatings, but not perfect)
Surface errors: 85% (manufacturing imperfections)
Tracking accuracy: 95% (solar tracking system accuracy)
Dust/soiling: 90% (regular maintenance assumed)

Combined realistic efficiency: {power_analysis.total_efficiency:.1%}

CORRECTED POWER ANALYSIS (1.2m diameter)
========================================
"""
    
    for condition, results in all_results.items():
        report_content += f"""
{condition.replace('_', ' ').title()}:
  Input irradiance: {results['irradiance']} W/m²
  Power density at 0.4m: {results['power_density_kW_m2']:.1f} kW/m²
  Total power collected: {results['realistic_power_W']:.0f} W
  Optical density: {results['optical_density']:.1f}x
"""
    
    report_content += f"""
COMPARISON WITH MY ORIGINAL VALUES
==================================
My original calculation (1361 W/m²): 13.6 kW/m² at 0.4m
AM1.5 Direct (900 W/m²): {all_results['am1_5_direct']['power_density_kW_m2']:.1f} kW/m² at 0.4m
Typical Clear Day (700 W/m²): {all_results['typical_clear_day']['power_density_kW_m2']:.1f} kW/m² at 0.4m

Overestimation:
- vs AM1.5: {(13.6 - all_results['am1_5_direct']['power_density_kW_m2']) / all_results['am1_5_direct']['power_density_kW_m2'] * 100:.0f}% too high
- vs Typical Day: {(13.6 - all_results['typical_clear_day']['power_density_kW_m2']) / all_results['typical_clear_day']['power_density_kW_m2'] * 100:.0f}% too high

RECOMMENDATIONS
===============
1. Use AM1.5 Direct Normal (900 W/m²) for design calculations
2. Use Peak Sun Conditions (1000 W/m²) for maximum performance
3. Use Typical Clear Day (700 W/m²) for average performance
4. Include 69% efficiency factor for realistic losses
5. Account for geographic and seasonal variations

CORRECTED DESIGN TARGETS
========================
For 10x optical density at 0.4m with 1.2m Fresnel lens:
- Realistic power density: {all_results['am1_5_direct']['power_density_kW_m2']:.1f} kW/m² (AM1.5)
- Realistic power collection: {all_results['am1_5_direct']['realistic_power_W']:.0f} W (AM1.5)
- Peak performance: {all_results['peak_sun_conditions']['power_density_kW_m2']:.1f} kW/m² (1000 W/m²)
- Conservative estimate: {all_results['typical_clear_day']['power_density_kW_m2']:.1f} kW/m² (700 W/m²)

GENERATED FILES
===============
realistic_power_comparison.png - Comparison visualization
REALISTIC_POWER_ANALYSIS_REPORT.txt - This report

CONCLUSION
==========
My original calculations overestimated power by 36-94% by using space
solar constant instead of realistic ground-level irradiance. The corrected
values show more achievable and practical performance expectations.
"""
    
    report_file = os.path.join(results_dir, 'REALISTIC_POWER_ANALYSIS_REPORT.txt')
    with open(report_file, 'w') as f:
        f.write(report_content.strip())
    
    print(f"✓ Comprehensive report saved: REALISTIC_POWER_ANALYSIS_REPORT.txt")
    
    print(f"\\n" + "="*80)
    print("REALISTIC POWER ANALYSIS COMPLETE")  
    print("="*80)
    print(f"All results saved in: {results_dir}")
    
    print(f"\\nKEY FINDINGS:")
    print(f"- I was using 1361 W/m² (space solar constant)")
    print(f"- Should use 700-1000 W/m² (realistic ground conditions)")
    print(f"- My power estimates were 36-94% too high!")
    print(f"- Realistic 10x at 0.4m: {all_results['am1_5_direct']['power_density_kW_m2']:.1f} kW/m² (not 13.6)")
    print(f"- Include {(1-power_analysis.total_efficiency)*100:.0f}% efficiency losses from real-world factors")


if __name__ == "__main__":
    create_power_comparison_analysis()