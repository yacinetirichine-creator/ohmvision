import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, MeshDistortMaterial, Float } from '@react-three/drei';

export function Hero3D() {
  const sphereRef = useRef();
  const lightRef = useRef();

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if(sphereRef.current) {
        sphereRef.current.rotation.x = t * 0.2;
        sphereRef.current.rotation.y = t * 0.3;
    }
    // Dynamic light movement
    if(lightRef.current) {
        lightRef.current.position.x = Math.sin(t) * 3;
        lightRef.current.position.z = Math.cos(t) * 3;
    }
  });

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight ref={lightRef} position={[2, 2, 2]} intensity={2} color="#00f0ff" />
      <pointLight position={[-2, -2, -2]} intensity={1} color="#bc13fe" />
      
      <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
        <mesh ref={sphereRef} scale={2}>
          <icosahedronGeometry args={[1, 1]} />
          <MeshDistortMaterial 
            color="#001020" 
            emissive="#00f0ff"
            emissiveIntensity={0.2}
            roughness={0.1}
            metalness={1}
            distort={0.4}
            speed={2}
            wireframe={true}
          />
        </mesh>
      </Float>
      
      {/* Core "Eye" */}
      <mesh scale={0.5}>
         <sphereGeometry args={[1, 32, 32]} />
         <meshStandardMaterial 
            color="#00f0ff"
            emissive="#00f0ff"
            emissiveIntensity={2}
            transparent
            opacity={0.8}
         />
      </mesh>
      
      {/* Particles or Orbiting elements could be added here */}
    </>
  );
}
