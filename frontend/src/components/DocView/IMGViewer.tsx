interface ImgViewerProps {
    file: Blob;
}
const IMGViewer: React.FC<ImgViewerProps> = ({ file }) => {
    const imageUrl = URL.createObjectURL(file);
    return (
        <div style={{ width: "100%" }}>
            <img src={imageUrl} alt="Imagen" />
        </div>
    );
};

export default IMGViewer;
