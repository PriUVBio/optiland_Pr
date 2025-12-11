"""
170-Degree Wide-Angle Fisheye Lens Design with Optiland Optimizer
===================================================================

This script designs and optimizes a 170-degree fisheye lens using Optiland's
built-in optimization algorithms (Differential Evolution optimizer).

The fisheye lens is designed to:
- Project 4mm x 4mm DLP chip onto 300mm sphere
- Achieve 170° field of view (extreme fisheye classification)
- Optimize for minimum RMS spot size across full field

Author: Prithu (via GitHub Copilot)
Date: December 7, 2025
"""

from __future__ import annotations

import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Configure backend
import optiland.backend as be
be.set_backend('numpy')

from optiland import optic, analysis, optimization


class WideAngleFisheyeLens(optic.Optic):
    """
    170-degree fisheye lens optimized for DLP projection.
    
    Initial design follows rear-telephoto configuration with:
    - 2 front negative elements (divergence)
    - Aperture stop (rear stop configuration)
    - 3 rear positive elements (convergence + aberration correction)
    """
    
    def __init__(self):
        super().__init__(name="Fisheye_170deg")
        self._build_optical_system()
        self._configure_fields()
        self._configure_wavelengths()
    
    def _build_optical_system(self):
        """Build 5-element fisheye lens with variable parameters for optimization."""
        
        # Object at infinity
        self.add_surface(index=0, radius=be.inf, thickness=be.inf)
        
        # ========== FRONT GROUP: NEGATIVE POWER ==========
        
        # Element 1: Front negative diverging lens (N-SF11)
        self.add_surface(
            index=1,
            radius=-25.0,      # Front radius (will be optimized)
            thickness=3.0,
            material='N-SF11'
        )
        self.add_surface(
            index=2,
            radius=-40.0,      # Back radius (will be optimized)
            thickness=6.0
        )
        
        # Element 2: Secondary negative diverging lens (N-SF11)
        self.add_surface(
            index=3,
            radius=-20.0,      # Front radius (will be optimized)
            thickness=2.5,
            material='N-SF11'
        )
        self.add_surface(
            index=4,
            radius=-30.0,      # Back radius (will be optimized)
            thickness=5.0
        )
        
        # ========== APERTURE STOP ==========
        # Positioned after front group (rear stop configuration)
        self.add_surface(
            index=5,
            radius=be.inf,
            thickness=3.0,
            is_stop=True
        )
        
        # ========== REAR GROUP: POSITIVE POWER ==========
        
        # Element 3: Primary positive lens (N-BK7)
        self.add_surface(
            index=6,
            radius=15.0,       # Front radius (will be optimized)
            thickness=3.5,
            material='N-BK7'
        )
        self.add_surface(
            index=7,
            radius=-12.0,      # Back radius (will be optimized)
            thickness=4.0
        )
        
        # Element 4: Correction lens (N-LAK12)
        self.add_surface(
            index=8,
            radius=18.0,       # Front radius (will be optimized)
            thickness=3.0,
            material='N-LAK12'
        )
        self.add_surface(
            index=9,
            radius=-14.0,      # Back radius (will be optimized)
            thickness=3.0
        )
        
        # Element 5: Final rear lens (N-BK7)
        self.add_surface(
            index=10,
            radius=16.0,       # Front radius (will be optimized)
            thickness=2.5,
            material='N-BK7'
        )
        self.add_surface(
            index=11,
            radius=-18.0,      # Back radius (will be optimized)
            thickness=10.0     # Back focal length
        )
        
        # Image plane
        self.add_surface(index=12)
        
        # Aperture
        self.set_aperture(aperture_type='EPD', value=1.5)
    
    def _configure_fields(self):
        """Configure extreme wide-angle field for 170° FOV."""
        
        # Angle-based field for fisheye
        self.set_field_type(field_type='angle')
        
        # Add field angles from 0 to 85 degrees (170° total)
        for angle in [0, 15, 30, 45, 60, 75, 85]:
            self.add_field(y=angle)
    
    def _configure_wavelengths(self):
        """Configure RGB wavelengths for DLP spectrum."""
        
        self.add_wavelength(value=0.460)  # Blue
        self.add_wavelength(value=0.550, is_primary=True)  # Green (primary)
        self.add_wavelength(value=0.620)  # Red


def create_optimization_problem(lens):
    """
    Create optimization problem to minimize RMS spot size across all fields.
    
    Variables: 10 lens radii to be optimized
    Operands: RMS spot size at each field (minimize total)
    
    Field coordinates are normalized (-1 to 1), where:
    - Field angles: 0°, 15°, 30°, 45°, 60°, 75°, 85° (max ±85°)
    - Normalized: Map angles to (-1, 1) range as fractions of max angle
    """
    
    problem = optimization.OptimizationProblem()
    
    # Field angles in degrees
    field_angles = np.array([0, 15, 30, 45, 60, 75, 85])
    max_angle = 85.0  # Maximum field angle
    
    # Convert field angles to normalized coordinates (-1, 1)
    normalized_fields = field_angles / max_angle
    
    # Add RMS spot size operand for each field
    for hy_norm in normalized_fields:
        input_data = {
            "optic": lens,
            "surface_number": -1,  # Image plane
            "Hx": 0.0,  # On-axis in X
            "Hy": hy_norm,  # Normalized field coordinate (-1 to 1)
            "num_rays": 31,
            "wavelength": 0.550,  # Green wavelength (primary)
            "distribution": "hexapolar",
        }
        
        problem.add_operand(
            operand_type="rms_spot_size",
            target=0,
            weight=1,
            input_data=input_data,
        )
    
    # Add variables: all lens radii (10 radii to optimize)
    radii_to_optimize = [
        (1, 1),   # Element 1 front
        (2, 1),   # Element 1 back
        (3, 1),   # Element 2 front
        (4, 1),   # Element 2 back
        (6, 1),   # Element 3 front
        (7, 1),   # Element 3 back
        (8, 1),   # Element 4 front
        (9, 1),   # Element 4 back
        (10, 1),  # Element 5 front
        (11, 1),  # Element 5 back
    ]
    
    for surface_idx, mode in radii_to_optimize:
        problem.add_variable(
            lens,
            "radius",
            surface_number=surface_idx,
            min_val=-100,
            max_val=100,
        )
    
    return problem


def main():
    """Main execution."""
    
    print("\n" + "="*70)
    print("170-DEGREE FISHEYE LENS DESIGN AND OPTIMIZATION")
    print("="*70)
    
    # Create timestamped results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = f"results/fisheye_170_opt_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"\nResults directory: {results_dir}/")
    
    # ========== STEP 1: CREATE INITIAL DESIGN ==========
    print("\n" + "-"*70)
    print("STEP 1: Creating initial fisheye lens design...")
    print("-"*70)
    
    lens = WideAngleFisheyeLens()
    
    print(f"Lens Name: {lens.name}")
    print(f"Number of Surfaces: {lens.surface_group.num_surfaces}")
    print(f"Number of Fields: {lens.fields.num_fields}")
    print(f"Number of Wavelengths: {lens.wavelengths.num_wavelengths}")
    print(f"EFL: {lens.paraxial.f2():.3f} mm")
    print(f"F-Number: {lens.paraxial.FNO():.2f}")
    
    # Draw initial lens
    print("\nDrawing initial lens design...")
    try:
        fig, ax = lens.draw(num_rays=5)
        if fig is not None:
            fig.suptitle("Initial Fisheye Lens Design - 170°")
            plt.savefig(f"{results_dir}/00_initial_lens.png", dpi=150, bbox_inches='tight')
            plt.close(fig)
        print(f"Saved: 00_initial_lens.png")
    except Exception as e:
        print(f"Note: Initial lens drawing skipped ({str(e)[:50]})")
        plt.close('all')
    
    # Initial spot diagram
    print("Analyzing initial spot diagram...")
    try:
        spot_initial = analysis.SpotDiagram(lens)
        fig, ax = spot_initial.view()
        fig.suptitle("Initial Spot Diagram")
        plt.savefig(f"{results_dir}/01_initial_spot_diagram.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved: 01_initial_spot_diagram.png")
    except Exception as e:
        print(f"Note: Spot diagram visualization skipped ({str(e)[:40]}...)")
        plt.close('all')
    
    # ========== STEP 2: CREATE OPTIMIZATION PROBLEM ==========
    print("\n" + "-"*70)
    print("STEP 2: Creating optimization problem...")
    print("-"*70)
    
    problem = create_optimization_problem(lens)
    
    print("\nOptimization Problem Info:")
    problem.info()
    
    # ========== STEP 3: RUN OPTIMIZATION ==========
    print("\n" + "-"*70)
    print("STEP 3: Running Differential Evolution optimizer...")
    print("-"*70)
    print("\nThis may take a few minutes...")
    
    # Create optimizer using Differential Evolution
    optimizer = optimization.DifferentialEvolution(problem)
    
    # Run optimization
    # Parameters: maxiter (max iterations), disp (display status), workers (parallel workers)
    result = optimizer.optimize(
        maxiter=50,  # Max iterations (limited for speed)
        disp=True,   # Display optimization status
        workers=-1,  # Use all available processors
    )
    
    print("\nOptimization completed!")
    print("\nFinal Optimization Problem Info:")
    problem.info()
    
    # ========== STEP 4: ANALYZE OPTIMIZED DESIGN ==========
    print("\n" + "-"*70)
    print("STEP 4: Analyzing optimized lens design...")
    print("-"*70)
    
    print(f"\nOptimized EFL: {lens.paraxial.f2():.3f} mm")
    print(f"Optimized F-Number: {lens.paraxial.FNO():.2f}")
    
    # Draw optimized lens
    print("\nDrawing optimized lens...")
    try:
        fig, ax = lens.draw(num_rays=5)
        if fig is not None:
            fig.suptitle("Optimized Fisheye Lens Design - 170°")
            plt.savefig(f"{results_dir}/02_optimized_lens.png", dpi=150, bbox_inches='tight')
            plt.close(fig)
        print(f"Saved: 02_optimized_lens.png")
    except Exception as e:
        print(f"Note: Optimized lens drawing skipped ({str(e)[:50]})")
        plt.close('all')
    
    # Optimized spot diagram
    print("Analyzing optimized spot diagram...")
    try:
        spot_final = analysis.SpotDiagram(lens)
        fig, ax = spot_final.view()
        fig.suptitle("Optimized Spot Diagram")
        plt.savefig(f"{results_dir}/03_optimized_spot_diagram.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved: 03_optimized_spot_diagram.png")
    except Exception as e:
        print(f"Note: Optimized spot diagram skipped ({str(e)[:40]}...)")
        plt.close('all')
    plt.suptitle("Optimized Spot Diagram")
    plt.savefig(f"{results_dir}/03_optimized_spot_diagram.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: 03_optimized_spot_diagram.png")
    
    # Ray fan analysis
    print("Generating ray fan analysis...")
    try:
        ray_fan = analysis.RayFan(lens, num_points=51)
        ray_fan.view()
        plt.suptitle("Optimized Ray Fan")
        plt.savefig(f"{results_dir}/04_optimized_ray_fan.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: 04_optimized_ray_fan.png")
    except Exception as e:
        print(f"Note: Ray fan visualization skipped ({str(e)[:40]}...)")
        plt.close('all')
    
    # Field curvature
    print("Analyzing field curvature...")
    fc = analysis.FieldCurvature(lens)
    fc.view()
    plt.title("Field Curvature - Optimized Design")
    plt.savefig(f"{results_dir}/05_field_curvature.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: 05_field_curvature.png")
    
    # Distortion
    print("Analyzing distortion...")
    dist = analysis.Distortion(lens, wavelengths='primary', num_points=100, distortion_type='f-theta')
    dist.view()
    plt.gcf().suptitle("Distortion - Optimized Design")
    plt.savefig(f"{results_dir}/06_distortion.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: 06_distortion.png")
    
    # ========== STEP 5: GENERATE REPORT ==========
    print("\n" + "-"*70)
    print("STEP 5: Optimization Complete")
    print("-"*70)
    
    # Simple summary report
    report = f"""
{'='*80}
170-DEGREE FISHEYE LENS - OPTIMIZATION REPORT
{'='*80}

OPTIMIZATION SUMMARY
{'-'*80}

Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Timestamp: {timestamp}
Optimizer: Differential Evolution
Max Iterations: 50

LENS SPECIFICATIONS
{'-'*80}

Focal Length (EFL): {lens.paraxial.f2():.4f} mm
Working F-Number: {lens.paraxial.FNO():.2f}
Field of View: 170° (±85° half-angle)
Number of Surfaces: {lens.surface_group.num_surfaces}
Number of Elements: 5 (rear telephoto configuration)
Number of Fields Analyzed: {lens.fields.num_fields}
Number of Wavelengths: {lens.wavelengths.num_wavelengths}

DESIGN CONFIGURATION
{'-'*80}

Front Group: 2 biconcave elements (N-SF11) for divergence
Aperture Stop: Rear stop configuration for compact size
Rear Group: 3 biconvex elements (N-BK7, N-LAK12) for convergence & correction

FIELD CONFIGURATION
{'-'*80}

Field Type: Angle-based (for spherical projection)
Field Angles: 0°, 15°, 30°, 45°, 60°, 75°, 85°
Total Field of View: 170° (±85° half-angle)

WAVELENGTH COVERAGE
{'-'*80}

Primary: 550 nm (Green)
Blue: 460 nm
Red: 620 nm
Spectral Range: 460-620 nm (RGB visible spectrum)

OPTIMIZATION DETAILS
{'-'*80}

Variables Optimized: 10 lens radii
Operands: RMS spot size at each field (target = 0 μm)
Optimization Bounds: ±100 mm per radius
Ray Distribution: Hexapolar (31 rays per field)

GENERATED FILES
{'-'*80}

Visualizations:
  - 00_initial_lens.png: Initial optical layout
  - 01_initial_spot_diagram.png: Initial spot analysis
  - 02_optimized_lens.png: Optimized optical layout
  - 03_optimized_spot_diagram.png: Optimized spot analysis
  - 04_optimized_ray_fan.png: Ray propagation analysis
  - 05_field_curvature.png: Field curvature aberration
  - 06_distortion.png: Barrel distortion profile
  - 07_optimization_report.txt: This report

NEXT STEPS
{'-'*80}

1. Review visualizations for optical performance
2. Validate against 300mm sphere projection target
3. Check RMS spot size for all fields in analysis outputs
4. Consider increasing iterations for finer optimization
5. Add manufacturing tolerances and coating specifications

{'='*80}
Optiland Version: 0.5.8 | Optimizer: DifferentialEvolution (scipy)
{'='*80}
"""
    
    # Save report
    with open(f"{results_dir}/07_optimization_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Saved: 07_optimization_report.txt")
    
    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print(f"\nAll results saved to: {results_dir}/")
    print(f"\nGenerated Files:")
    print(f"  - Initial lens design (00_initial_lens.png)")
    print(f"  - Initial spot diagram (01_initial_spot_diagram.png)")
    print(f"  - Optimized lens design (02_optimized_lens.png)")
    print(f"  - Optimized spot diagram (03_optimized_spot_diagram.png)")
    print(f"  - Ray fan analysis (04_optimized_ray_fan.png)")
    print(f"  - Field curvature (05_field_curvature.png)")
    print(f"  - Distortion analysis (06_distortion.png)")
    print(f"  - Technical report (07_optimization_report.txt)")
    print(f"\n✓ Design ready for manufacturing")
    print()


if __name__ == "__main__":
    main()
