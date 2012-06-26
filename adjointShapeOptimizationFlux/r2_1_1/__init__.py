#!/usr/bin/env python

#--------------------------------------------------------------------------------------
## pythonFlu - Python wrapping for OpenFOAM C++ API
## Copyright (C) 2010- Alexey Petrov
## Copyright (C) 2009-2010 Pebble Bed Modular Reactor (Pty) Limited (PBMR)
## 
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
## 
## See http://sourceforge.net/projects/pythonflu
##
## Author : Alexey PETROV, Andrey SIMURZIN
##


#------------------------------------------------------------------------------------
from Foam import ref, man


#------------------------------------------------------------------------------------
def createPhia( runTime, mesh, Ua ):
    ref.ext_Info() << "Reading/calculating face flux field phia\n" << ref.nl

    phia = man.surfaceScalarField( man.IOobject( ref.word( "phia" ),
                                                 ref.fileName( runTime.timeName() ),
                                                 mesh,
                                                 ref.IOobject.READ_IF_PRESENT,
                                                 ref.IOobject.AUTO_WRITE ),
                                   man.surfaceScalarField( ref.linearInterpolate( Ua ) & mesh.Sf(), man.Deps( Ua, mesh ) ) );
    
    return phia

#------------------------------------------------------------------------------------
def zeroCells( vf, cells ):
    from Foam.template import GeometricField
    
    value = None
    if vf.__class__ == GeometricField( ref.scalar, ref.volMesh ) or vf.__class__ == man.GeometricField( ref.scalar, ref.volMesh ) :
       value = 0.0

    if vf.__class__ == GeometricField( ref.vector, ref.volMesh ) or vf.__class__ == man.GeometricField( ref.vector, ref.volMesh ):
       value = ref.vector( 0.0, 0.0, 0.0 )

    for element in range( cells.size() ):
         vf[ cells[ element ] ] = value
         pass
    pass


#------------------------------------------------------------------------------------
def createFields( runTime, mesh ):
    # Load boundary conditions
    import adjointOutletPressure
    import adjointOutletVelocity

    ref.ext_Info() << "Reading field p\n" << ref.nl
    p = man.volScalarField( man.IOobject( ref.word( "p" ),
                                          ref.fileName( runTime.timeName() ),
                                          mesh,
                                          ref.IOobject.MUST_READ,
                                          ref.IOobject.AUTO_WRITE ),
                            mesh )

    ref.ext_Info() << "Reading field U\n" << ref.nl
    U = man.volVectorField( man.IOobject( ref.word( "U" ),
                                          ref.fileName( runTime.timeName() ),
                                          mesh,
                                          ref.IOobject.MUST_READ,
                                          ref.IOobject.AUTO_WRITE ),
                            mesh )

    phi = man.createPhi( runTime, mesh, U )

    pRefCell = 0
    pRefValue = 0.0
    ref.setRefCell( p, mesh.solutionDict().subDict( ref.word( "SIMPLE" ) ), pRefCell, pRefValue )

    ref.ext_Info() << "Reading field pa\n" << ref.nl
    pa = man.volScalarField( man.IOobject( ref.word( "pa" ),
                                           ref.fileName( runTime.timeName() ),
                                           mesh,
                                           ref.IOobject.MUST_READ,
                                           ref.IOobject.AUTO_WRITE ),
                             mesh )

    ref.ext_Info() << "Reading field Ua\n" << ref.nl
    Ua = man.volVectorField( man.IOobject( ref.word( "Ua" ),
                                           ref.fileName( runTime.timeName() ),
                                           mesh,
                                           ref.IOobject.MUST_READ,
                                           ref.IOobject.AUTO_WRITE ),
                             mesh )

    phia = createPhia( runTime, mesh, Ua )

    paRefCell = 0
    paRefValue = 0.0
    ref.setRefCell( pa, mesh.solutionDict().subDict( ref.word( "SIMPLE" ) ), paRefCell, paRefValue )

    laminarTransport = man.singlePhaseTransportModel( U, phi )

    turbulence = man.incompressible.RASModel.New( U, phi, laminarTransport )

    zeroSensitivity = ref.dimensionedScalar( ref.word( "0" ), ref.dimVelocity * ref.dimVelocity, 0.0 )
    zeroAlpha = ref.dimensionedScalar ( ref.word( "0" ), ref.dimless / ref.dimTime, 0.0 )

    lambda_ = ref.dimensionedScalar( laminarTransport.lookup( ref.word( "lambda" ) ) )
    alphaMax = ref.dimensionedScalar( laminarTransport.lookup( ref.word( "alphaMax" ) ) )

    inletCells = mesh.boundary()[ ref.word( "inlet" ) ].faceCells()
    # outletCells = mesh.boundary()[ ref.word( "outlet" ) ].faceCells()

    alpha = man.volScalarField( man.IOobject( ref.word( "alpha" ),
                                              ref.fileName( runTime.timeName() ),
                                              mesh,
                                              ref.IOobject.READ_IF_PRESENT,
                                              ref.IOobject.AUTO_WRITE ),
                                lambda_ *  ( Ua & U ).ext_max( zeroSensitivity ) )
    
    zeroCells( alpha, inletCells )
    # zeroCells( alpha, outletCells )
    
    return p, U, phi, pa, Ua, phia, alpha, laminarTransport, turbulence, zeroSensitivity, zeroAlpha, \
           lambda_, alphaMax, inletCells, pRefCell, pRefValue, paRefCell, paRefValue
    
    
#------------------------------------------------------------------------------------
def initAdjointContinuityErrs():
    cumulativeAdjointContErr = 0.0
    
    return cumulativeAdjointContErr


#------------------------------------------------------------------------------------
def adjointContinuityErrs( runTime, mesh, phia, cumulativeAdjointContErr ):
     sumLocalContErr = runTime.deltaTValue() * ref.fvc.div( phia ).mag().weightedAverage( mesh.V() ).value()
     
     globalContErr = runTime.deltaTValue() * ref.fvc.div( phia ).weightedAverage( mesh.V() ).value()
     
     cumulativeAdjointContErr += globalContErr
     
     ref.ext_Info() << "Adjoint continuity errors : sum local = " << sumLocalContErr << ", global = " << globalContErr \
                    << ", cumulative = " << cumulativeAdjointContErr << ref.nl
     
     return cumulativeAdjointContErr


#------------------------------------------------------------------------------------
def main_standalone( argc, argv ):

    args = ref.setRootCase( argc, argv )

    runTime = man.createTime( args )
    
    mesh = man.createMesh( runTime )
    
    p, U, phi, pa, Ua, phia, alpha, laminarTransport, turbulence, zeroSensitivity, zeroAlpha, \
           lambda_, alphaMax, inletCells, pRefCell, pRefValue, paRefCell, paRefValue = createFields( runTime, mesh )

    cumulativeContErr = ref.initContinuityErrs()
    
    cumulativeAdjointContErr = initAdjointContinuityErrs()
    
    simple = man.simpleControl( mesh )
    
    ref.ext_Info() << "\nStarting time loop\n" << ref.nl
    
    while simple.loop() :
        ref.ext_Info()<< "Time = " << runTime.timeName() << ref.nl << ref.nl
        
        laminarTransport.lookup( ref.word( "lambda" ) ) >> lambda_
        
        alpha += mesh.fieldRelaxationFactor( ref.word( "alpha" ) ) * ( ( ( alpha + lambda_ * ( Ua & U ) ).ext_max( zeroAlpha ) ).ext_min( alphaMax ) - alpha);

        zeroCells( alpha, inletCells )
        
        UEqn = ref.fvm.div( phi, U ) + turbulence.divDevReff( U ) + ref.fvm.Sp( alpha, U )
        
        UEqn.relax()
        ref.solve( UEqn == -ref.fvc.grad( p ) )

        p.ext_boundaryField().updateCoeffs()
        
        rAU = 1.0 / UEqn.A()
        U << rAU * UEqn.H()

        phi << ( ref.fvc.interpolate( U ) & mesh.Sf() );
        ref.adjustPhi(phi, U, p)
        
        while simple.correctNonOrthogonal():
            pEqn = ref.fvm.laplacian( rAU, p ) == ref.fvc.div( phi )

            pEqn.setReference( pRefCell, pRefValue )
            pEqn.solve()

            if simple.finalNonOrthogonalIter():
                phi -= pEqn.flux()
                pass
            pass

        cumulativeContErr = ref.ContinuityErrs( phi, runTime, mesh, cumulativeContErr )
        
        # Explicitly relax pressure for momentum corrector
        p.relax();
        # Momentum corrector
        U -= rAU * ref.fvc.grad( p )
        U.correctBoundaryConditions()

        # Adjoint Pressure-velocity SIMPLE corrector
        # Adjoint Momentum predictor

        adjointTransposeConvection = ( ref.fvc.grad( Ua ) & U )
        # adjointTransposeConvection = ref.fvc.reconstruct( mesh.magSf() * ( ref.fvc.snGrad( Ua ) & ref.fvc.interpolate( U ) ) )
        zeroCells( adjointTransposeConvection, inletCells )

        UaEqn = ref.fvm.div( -phi, Ua ) - adjointTransposeConvection + turbulence.divDevReff( Ua ) + ref.fvm.Sp( alpha, Ua )

        UaEqn.relax()
        ref.solve( UaEqn == -ref.fvc.grad( pa ) )
        pa.ext_boundaryField().updateCoeffs()

        rAUa = 1.0 / UaEqn.A()
        Ua << rAUa * UaEqn.H()
        
        UaEqn.clear()
        phia << ( ref.fvc.interpolate( Ua ) & mesh.Sf() )
        
        ref.adjustPhi( phia, Ua, pa )

        # Non-orthogonal pressure corrector loop
        while simple.correctNonOrthogonal():
            paEqn = ref.fvm.laplacian( rAUa, pa ) == ref.fvc.div( phia )
            paEqn.setReference( paRefCell, paRefValue )
            paEqn.solve()
            
            if simple.finalNonOrthogonalIter():
                phia -= paEqn.flux()
                pass
            pass

        cumulativeAdjointContErr = adjointContinuityErrs( runTime, mesh, phia, cumulativeAdjointContErr )
        
        # Explicitly relax pressure for adjoint momentum corrector
        pa.relax();

        # Adjoint momentum corrector
        Ua -= rAUa * ref.fvc.grad(pa)
        Ua.correctBoundaryConditions()
        
        turbulence.correct()
        
        runTime.write()

        ref.ext_Info()<< "ExecutionTime = " << runTime.elapsedCpuTime() << " s\n\n" \
                      << ref.nl
        pass

    ref.ext_Info() << "End\n" << ref.nl
    
    import os
    return os.EX_OK

    
#--------------------------------------------------------------------------------------
argv = None
import sys, os
from Foam import FOAM_VERSION
if FOAM_VERSION( ">=", "020101" ):
    if __name__ == "__main__" :
        argv = sys.argv
        os._exit( main_standalone( len( argv ), argv ) )
        pass
else:
    ref.ext_Info() << "\n\n To use this solver, it is necessary to SWIG OpenFOAM-2.1.1 or higher \n"    
    pass


#--------------------------------------------------------------------------------------

