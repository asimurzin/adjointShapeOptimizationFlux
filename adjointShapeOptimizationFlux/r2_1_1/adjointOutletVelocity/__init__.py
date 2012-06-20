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
fixedValueFvPatchVectorField = ref.fixedValueFvPatchVectorField


#------------------------------------------------------------------------------------
class adjointOutletVelocityFvPatchVectorField( fixedValueFvPatchVectorField ):
    def __init__( self, *args ):
        try:
            self._init__fvPatch__DimensionedField_vector_volMesh( *args )
            return
        except AssertionError:
            pass
        except Exception:
            import sys, traceback
            traceback.print_exc( file = sys.stdout )
            pass
        
        try:
            self._init__fvPatch__DimensionedField_vector_volMesh__dictionary( *args )
            return
        except AssertionError:
            pass
        except Exception:
            import sys, traceback
            traceback.print_exc( file = sys.stdout )
            pass

        try:
            self._init__self__DimensionedField_vector_volMesh( *args )
            return
        except AssertionError:
            pass
        except Exception:
            import sys, traceback
            traceback.print_exc( file = sys.stdout )
            pass
        
        raise AssertionError()

    #------------------------------------------------------------------------------------
    def type( self ) :
        return ref.word( "adjointOutletVelocity" )
    
    
    #------------------------------------------------------------------------------------
    def _init__fvPatch__DimensionedField_vector_volMesh( self, *args ) :
        if len( args ) != 2 :
            raise AssertionError( "len( args ) != 2" )
        argc = 0

        try:
            ref.fvPatch.ext_isinstance( args[ argc ] )
        except TypeError:
            raise AssertionError( "args[ argc ].__class__ != fvPatch" )
        p = args[ argc ]; argc += 1
        
        try:
            ref.DimensionedField_vector_volMesh.ext_isinstance( args[ argc ] )
        except TypeError:
            raise AssertionError( "args[ argc ].__class__ != DimensionedField_vector_volMesh" )
        iF = args[ argc ]; argc += 1
        
        fixedValueFvPatchVectorField.__init__( self, p, iF )
        
        return self
        
    #------------------------------------------------------------------------------------
    def _init__fvPatch__DimensionedField_vector_volMesh__dictionary( self, *args ) :
        if len( args ) != 3 :
            raise AssertionError( "len( args ) != 3" )
        argc = 0
        
        try:
            ref.fvPatch.ext_isinstance( args[ argc ] )
        except TypeError:
            raise AssertionError( "args[ argc ].__class__ != fvPatch" )
        p = args[ argc ]; argc += 1
        
        try:
            ref.DimensionedField_vector_volMesh.ext_isinstance( args[ argc ] )
        except TypeError:
            raise AssertionError( "args[ argc ].__class__ != DimensionedField_vector_volMesh" )
        iF = args[ argc ]; argc += 1
        
        try:
            ref.dictionary.ext_isinstance( args[ argc ] )
        except TypeError:
            raise AssertionError( "args[ argc ].__class__ != dictionary" )
        dict_ = args[ argc ]; argc += 1
        
        fixedValueFvPatchVectorField.__init__( self, p, iF )
       
        ref.fvPatchVectorField.__lshift__( self, ref.vectorField( ref.word( "value" ), dict_, p.size() ) )
        
        return self

        
    #------------------------------------------------------------------------------------
    def _init__self__DimensionedField_vector_volMesh( self, *args ) :
        if len( args ) != 2 :
            raise AssertionError( "len( args ) != 3" )
        argc = 0

        if args[ argc ].__class__ != self.__class__ :
            raise AssertionError( "args[ argc ].__class__ != self.__class__" )
        wtcsf = args[ argc ]; argc += 1
        
        try:
            ref.DimensionedField_vector_volMesh.ext_isinstance( args[ argc ] )
        except TypeError:
            raise AssertionError( "args[ argc ].__class__ != DimensionedField_vector_volMesh" )
        iF = args[ argc ]; argc += 1

        fixedValueFvPatchVectorField.__init__( self, wtcsf, iF )

        return self
        
    #------------------------------------------------------------------------------------
    def write( self, os ) :
        ref.fvPatchVectorField.write( self, os )

        self.writeEntry( ref.word( "value" ), os )
        pass

    #------------------------------------------------------------------------------------
    def updateCoeffs( self ) :
        try:
            if self.updated() :
                return
            
            phiap = ref.surfaceScalarField.ext_lookupPatchField( self.patch(), ref.word( "phia" ) )
            Up = ref.volVectorField.ext_lookupPatchField( self.patch(), ref.word( "U" ) )
            Un = ( self.patch().nf() & Up ).mag()
            UtHat = ( ( Up - self.patch().nf() * Un ) / ( Un + ref.SMALL ) )
            Uan = ( self.patch().nf() * ( self.patch().nf() & self.patchInternalField() ) )

            ref.vectorField.__lshift__( self, phiap * self.patch().Sf() / self.patch().magSf().sqr() + UtHat )
            # vectorField::operator=(Uan + UtHat);
            fixedValueFvPatchVectorField.updateCoeffs( self )
            pass
        except Exception, exc:
            import sys, traceback
            traceback.print_exc( file = sys.stdout )
            raise exc
        pass
    
    #-------------------------------------------------------------------------------------
    def clone( self, *args ) :
        try:
            return self._clone( *args )
        except AssertionError:
            pass
        except Exception:
            import sys, traceback
            traceback.print_exc( file = sys.stdout )
            pass
        
        try:
            return self._clone__DimensionedField_vector_volMesh( *args )
        except AssertionError :
            pass
        except Exception:
            import sys, traceback
            traceback.print_exc( file = sys.stdout )
            pass
        
        raise AssertionError()
           
    #------------------------------------------------------------------------------------
    def _clone( self, *args ) :
        if len( args ) != 0 :
            raise AssertionError( "len( args ) != 0" )

        obj = adjointOutletVelocityFvPatchVectorField( self )

        return ref.tmp_fvPatchField_vector( obj )
        
    #------------------------------------------------------------------------------------
    def _clone__DimensionedField_vector_volMesh( self, *args ) :
        if len( args ) != 1 :
            raise AssertionError( "len( args ) != 1" )
        argc = 0

        try:
            ref.DimensionedField_vector_volMesh.ext_isinstance( args[ argc ] )
        except TypeError:
            raise AssertionError( "args[ argc ].__class__ != DimensionedField_scalar_volMesh" )
        iF = args[ argc ]; argc += 1

        obj = adjointOutletVelocityFvPatchVectorField( self, iF )
        
        return ref.tmp_fvPatchField_vector( obj )
        
    #------------------------------------------------------------------------------------
    pass


#------------------------------------------------------------------------------------
from Foam.template import getfvPatchFieldConstructorToTableBase_vector

class fvPatchFieldConstructorToTable_adjointOutletVelocity( getfvPatchFieldConstructorToTableBase_vector() ):

    def __init__( self ):
        aBaseClass = self.__class__.__mro__[ 1 ]
        aBaseClass.__init__( self )
        
        aBaseClass.init( self, self, ref.word( "adjointOutletVelocity" ) )
        pass
    
    def new_patch( self, p, iF ):
        obj = adjointOutletVelocityFvPatchVectorField( p,iF )
        
        return ref.tmp_fvPatchField_vector( obj )

    def new_patchMapper( self, ptf , p, iF, m ):
        obj = adjointOutletVelocityFvPatchVectorField( ptf , p, iF, m )

        return ref.tmp_fvPatchField_vector( obj )
    
    def new_dictionary( self, p, iF, dict_ ):
        obj = adjointOutletVelocityFvPatchVectorField( p, iF, dict_ )
        
        return ref.tmp_fvPatchField_vector( obj )
            
    pass

      
#----------------------------------------------------------------------------------------------------------
adjointOutletVelocity_fvPatchFieldConstructorToTable = fvPatchFieldConstructorToTable_adjointOutletVelocity()


#----------------------------------------------------------------------------------------------------------
