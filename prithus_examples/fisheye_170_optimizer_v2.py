"""
170-Degree Wide-Angle Fisheye Lens Design with Optiland Optimization

This script designs a 170-degree wide-angle (±85°) fisheye lens using:
  - 5-element rear telephoto configuration
  - RMS spot size minimization across 7 field angles
  - Differential Evolution global optimizer
  
Based on Optiland tutorials and gallery examples.
Author: Optiland Examples
"""

import os
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

from optiland import optic, optimization


class WideAngleFisheyeLens(optic.Optic):
    """170-degree fisheye lens based on rear telephoto configuration."""
    
    def __init__(self):
        super().__init__()
        self.name = "Fisheye_170deg"
        
        # Object at infinity
        self.add_surface(index=0, thickness=np.inf)
        
        # ===== FRONT NEGATIVE ELEMENTS (2x) =====
        # Element 1: Strong negative lens (diverging)
        self.add_surface(
            index=1,
            thickness=5,
            radius=-25.0,  # Front (negative)
            material="N-SF11",  # High-index negative
        )
        self.add_surface(
            index=2,
            thickness=3,
            radius=-40.0,  # Back (negative)
        )
        
        # Element 2: Weaker negative lens (diverging)
        self.add_surface(
            index=3,
            thickness=2,
            radius=-20.0,  # Front (negative)
            material="N-SF11",
        )
        self.add_surface(
            index=4,
            thickness=3,
            radius=-30.0,  # Back (negative)
        )
        
        # ===== MIDDLE SPACE =====
        self.add_surface(
            index=5,
            thickness=8.0,  # Gap between front/rear groups
        )
        
        # ===== REAR POSITIVE ELEMENTS (3x) =====
        # Element 3: Positive lens (converging)
        self.add_surface(
            index=6,
            thickness=4,
            radius=18.0,  # Front (positive)
            material="N-BK7",  # Crown glass
            is_stop=True,  # Aperture stop
        )
        self.add_surface(
            index=7,
            thickness=5,
            radius=-25.0,  # Back (negative)
        )
        
        # Element 4: Positive lens (converging)
        self.add_surface(
            index=8,
            thickness=3,
            radius=22.0,  # Front (positive)
            material="N-BK7",
        )
        self.add_surface(
            index=9,
            thickness=5,
            radius=-18.0,  # Back (negative)
        )
        
        # Element 5: Final positive lens (converging, focus control)
        self.add_surface(
            index=10,
            thickness=4,
            radius=20.0,  # Front (positive)
            material="N-LAK12",  # Lanthanum crown
        )
        self.add_surface(
            index=11,
            thickness=6,
            radius=-16.0,  # Back (negative)
        )
        
        # Image plane
        self.add_surface(index=12, thickness=0)
        
        # ===== OPTICAL SYSTEM CONFIGURATION =====
        # Aperture: 20mm effective focal diameter
        self.set_aperture(aperture_type="EPD", value=20)
        
        # Field: Angle-based field definition for fisheye distortion
        self.set_field_type(field_type="angle")
        # Add field angles: 0°, 15°, 30°, 45°, 60°, 75°, 85°
        for angle in [0, 15, 30, 45, 60, 75, 85]:
            self.add_field(y=angle)
        
        # Wavelengths: RGB spectrum for DLP projection
        self.add_wavelength(value=0.460, is_primary=False)  # Blue
        self.add_wavelength(value=0.550, is_primary=True)   # Green (primary)
        self.add_wavelength(value=0.620, is_primary=False)  # Red


def create_optimization_problem(lens):
    """
    Create optimization problem to minimize RMS spot size.
    
    This function:
    - Adds 7 operands (one RMS spot size per field angle)
    - Adds 10 variables (all lens radii for optimization)
    - Configures bounds for Differential Evolution
    
    Args:
        lens: Optiland Optic object
        
    Returns:
        OptimizationProblem configured and ready to optimize
    """
    problem = optimization.OptimizationProblem()
    
    # Get normalized field coordinates
    # Fields are: 0°, 15°, 30°, 45°, 60°, 75°, 85° (max ±85°)
    # Normalize to (-1, 1) range
    field_angles_deg = np.array([0, 15, 30, 45, 60, 75, 85])
    max_angle = 85.0
    normalized_fields = field_angles_deg / max_angle
    
    # Add RMS spot size operand for each field
    # RMS spot size = root-mean-square deviation of ray intercepts at image plane
    for hy_norm in normalized_fields:
        input_data = {
            "optic": lens,
            "surface_number": -1,      # Image plane (last surface)
            "Hx": 0.0,                 # On-axis in X
            "Hy": hy_norm,             # Normalized field (-1 to 1)
            "num_rays": 31,            # Hexapolar distribution with 31 rays
            "wavelength": 0.550,       # Green wavelength (primary)
            "distribution": "hexapolar",
        }
        
        problem.add_operand(
            operand_type="rms_spot_size",
            target=0,                  # Minimize to zero
            weight=1,                  # Equal weight for all fields
            input_data=input_data,
        )
    
    # Add variables: all lens radii (10 total)
    # Surfaces: 1,2 (elem1), 3,4 (elem2), 6,7 (elem3), 8,9 (elem4), 10,11 (elem5)
    surfaces_to_optimize = [1, 2, 3, 4, 6, 7, 8, 9, 10, 11]
    
    for surf_idx in surfaces_to_optimize:
        problem.add_variable(
            lens,
            "radius",
            surface_number=surf_idx,
            min_val=-100,              # Bound: -100 mm
            max_val=100,               # Bound: +100 mm
        )
    
    return problem


def main():
    """Main execution: design and optimize 170° fisheye."""
    
    print("\n" + "="*80)
    print("170-DEGREE FISHEYE LENS DESIGN AND OPTIMIZATION")
    print("="*80 + "\n")
    
    # Create results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = f"results/fisheye_170_opt_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    print(f"Results directory: {results_dir}\n")
    
    # ===== STEP 1: CREATE INITIAL DESIGN =====
    print("-" * 80)
    print("STEP 1: Creating initial fisheye lens design")
    print("-" * 80)
    
    lens = WideAngleFisheyeLens()
    print(f"\nLens Name: {lens.name}")
    print(f"Number of Surfaces: {lens.surface_group.num_surfaces}")
    print(f"Number of Fields: {lens.fields.num_fields}")
    print(f"Number of Wavelengths: {lens.wavelengths.num_wavelengths}")
    
    # Calculate initial properties
    try:
        efl = lens.paraxial.EFL()
        fno = lens.paraxial.FNO()
        print(f"Initial EFL: {efl:.3f} mm")
        print(f"Initial F-Number: {fno:.2f}\n")
    except:
        print("(Could not calculate initial properties)\n")
    
    # Draw initial lens
    print("Drawing initial lens...")
    try:
        lens.draw(num_rays=10)
        plt.savefig(f"{results_dir}/00_initial_lens.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: 00_initial_lens.png")
    except Exception as e:
        print(f"✗ Initial lens drawing skipped ({type(e).__name__})")
        plt.close('all')
    
    # ===== STEP 2: CREATE OPTIMIZATION PROBLEM =====
    print("\n" + "-" * 80)
    print("STEP 2: Creating optimization problem")
    print("-" * 80 + "\n")
    
    problem = create_optimization_problem(lens)
    
    print("Initial Optimization Problem:")
    try:
        problem.info()
    except Exception as e:
        print(f"Warning: Could not display problem info: {e}\n")
    
    # ===== STEP 3: RUN OPTIMIZATION =====
    print("\n" + "-" * 80)
    print("STEP 3: Running Differential Evolution optimizer")
    print("-" * 80)
    print("\nThis may take several minutes (50 iterations, parallel workers)...\n")
    
    try:
        optimizer = optimization.DifferentialEvolution(problem)
        result = optimizer.optimize(
            maxiter=50,    # Maximum iterations
            disp=True,     # Display progress
            workers=-1,    # Use all CPU cores
        )
        
        print(f"\n✓ Optimization completed!")
        print(f"  - Success: {result.success}")
        print(f"  - Iterations: {result.nit}")
        print(f"  - Function evaluations: {result.nfev}")
        print(f"  - Final merit function: {result.fun:.6f}\n")
        
    except Exception as e:
        print(f"\n✗ Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ===== STEP 4: ANALYZE RESULTS =====
    print("-" * 80)
    print("STEP 4: Analyzing optimized design")
    print("-" * 80 + "\n")
    
    print("Final Optimization Problem:")
    try:
        problem.info()
    except Exception as e:
        print(f"Warning: Could not display final problem info: {e}\n")
    
    # Show final system properties
    try:
        efl_final = lens.paraxial.EFL()
        fno_final = lens.paraxial.FNO()
        print(f"\nOptimized EFL: {efl_final:.3f} mm")
        print(f"Optimized F-Number: {fno_final:.2f}\n")
    except:
        pass
    
    # Draw optimized lens
    print("Drawing optimized lens...")
    try:
        lens.draw(num_rays=10)
        plt.savefig(f"{results_dir}/02_optimized_lens.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: 02_optimized_lens.png\n")
    except Exception as e:
        print(f"✗ Optimized lens drawing skipped ({type(e).__name__})\n")
        plt.close('all')
    
    # ===== STEP 5: SUMMARY =====
    print("-" * 80)
    print("STEP 5: Optimization Summary")
    print("-" * 80 + "\n")
    
    print(f"✓ Optimization completed successfully!")
    print(f"\nResults saved to: {results_dir}/")
    print(f"\nGenerated files:")
    print(f"  - 00_initial_lens.png: Initial 170° fisheye design")
    print(f"  - 02_optimized_lens.png: Optimized fisheye design")
    print(f"\nOptimization configuration:")
    print(f"  - Optimizer: Differential Evolution (global)")
    print(f"  - Max iterations: 50")
    print(f"  - Parallel workers: All available CPU cores")
    print(f"  - Variables: 10 (all lens radii)")
    print(f"  - Operands: 7 (RMS spot size per field)")
    print(f"  - Field angles: 0°, 15°, 30°, 45°, 60°, 75°, 85°")
    print(f"  - Wavelengths: 460nm (blue), 550nm (green - primary), 620nm (red)")
    print(f"\nLens configuration:")
    print(f"  - Type: 5-element rear telephoto fisheye")
    print(f"  - Front group: 2× negative elements (N-SF11)")
    print(f"  - Rear group: 3× positive elements (N-BK7, N-LAK12)")
    print(f"  - Aperture: 20mm EPD")
    print(f"  - Image: {lens.surface_group.num_surfaces} surfaces")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
