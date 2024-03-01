interface ImgViewerProps {
    file: Blob;
}
const IMGViewer: React.FC<ImgViewerProps> = ({ file }) => {
    const imageUrl = URL.createObjectURL(file);
    return (
        <div>
            <img src={imageUrl} alt="Imagen" />
        </div>
    );
};

export default IMGViewer;
