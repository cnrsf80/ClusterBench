///<reference path="babylon.d.ts" />

import float = BABYLON.float;

const _VISIBLE=0.9
const _HIDDEN=0.1

class Game {

    private spheres:any[]=[];

    private _canvas: HTMLCanvasElement;
    private _engine: BABYLON.Engine;
    private _scene: BABYLON.Scene;
    private _camera: BABYLON.ArcRotateCamera;
    private _light1: BABYLON.Light;
    private _light2: BABYLON.Light;
    private _actionManager:BABYLON.ActionManager;

    constructor(canvasElement : string) {
        // Create canvas and engine.
        this._canvas = document.getElementById(canvasElement) as HTMLCanvasElement;
        this._engine = new BABYLON.Engine(this._canvas, true);
    }

    prepareButton(mesh) {
        mesh.actionManager = new BABYLON.ActionManager(this._scene);
        mesh.actionManager.registerAction(
            new BABYLON.ExecuteCodeAction(
                {
                    trigger: BABYLON.ActionManager.OnPickTrigger
                },
                (evt) => {
                    let target:any=evt.meshUnderPointer;

                    let target_alpha=_VISIBLE;
                    if(target.material.alpha==_VISIBLE) {
                        for (let s of this.spheres) {
                            if (s.cluster_name != target.cluster_name) s.material.alpha = _HIDDEN;
                        }
                    }else
                        for(let s of this.spheres)
                            s.material.alpha=_VISIBLE;

                }
            )
        )
    }

    createMesure(name:string,cluster_name:string,x:float,y:float,z:float,color:BABYLON.Color3,expense:float):void {
        var materialSphere = new BABYLON.StandardMaterial("texture2", this._scene);
        materialSphere.diffuseColor = color;
        materialSphere.alpha = 0.9;

        let sphere:any = BABYLON.MeshBuilder.CreateSphere(name,{segments: 16, diameter: 2}, this._scene);

        sphere.position.x = (x-0.5)*expense;
        sphere.position.y = (y-0.5)*expense;
        sphere.position.z = (z-0.5)*expense;
        sphere.material=materialSphere;
        sphere.cluster_name=cluster_name;

        this.prepareButton(sphere);
        this.spheres.push(sphere);
    }

    createScene() : void {
        // Create a basic BJS Scene object.
        this._scene = new BABYLON.Scene(this._engine);
        this._scene.fogMode = BABYLON.Scene.FOGMODE_EXP
        this._scene.fogDensity = 0.01;
        this._scene.fogColor = new BABYLON.Color3(0.9, 0.9, 0.85);

        // Create a FreeCamera, and set its position to (x:0, y:5, z:-10).
        this._camera = new BABYLON.ArcRotateCamera("Camera", 3 * Math.PI / 2, Math.PI / 8, 50, BABYLON.Vector3.Zero(), this._scene);

        this._actionManager = new BABYLON.ActionManager(this._scene);

        // Target the camera to scene origin.
        this._camera.setTarget(BABYLON.Vector3.Zero());

        // Attach the camera to the canvas.
        this._camera.attachControl(this._canvas, false);

        // Create a basic light, aiming 0,1,0 - meaning, to the sky.
        this._light1 = new BABYLON.HemisphericLight('light1', new BABYLON.Vector3(0,0,-1), this._scene);
        //this._light2 = new BABYLON.HemisphericLight('light2', new BABYLON.Vector3(0,1,0), this._scene);


        // Move the sphere upward 1/2 of its height.

        for(var i=0;i<150;i++){
            this.createMesure("spere"+i,"cluster"+(i % 10),Math.random(),Math.random(),Math.random(),new BABYLON.Color3(Math.random(), Math.random(), Math.random()),40)
        }

        // Create a built-in "ground" shape.
        //let ground = BABYLON.MeshBuilder.CreateGround('ground1',{width: 6, height: 6, subdivisions: 2}, this._scene);
    }

    doRender() : void {
        // Run the render loop.
        this._engine.runRenderLoop(() => {
            this._scene.render();
        });

        // The canvas/window resize event handler.
        window.addEventListener('resize', () => {
            this._engine.resize();
        });
    }
}

window.addEventListener('DOMContentLoaded', () => {
    // Create the game using the 'renderCanvas'.
    let game = new Game('renderCanvas');

    // Create the scene.
    game.createScene();

    // Start render loop.
    game.doRender();
});